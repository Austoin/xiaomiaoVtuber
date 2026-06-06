import type { XiaomiaoBridgeState } from './xiaomiao-bridge'

import { shouldAdoptXiaomiaoBridgeState } from './xiaomiao-bridge'

export interface BridgeSpeechVoice {
  id: string
  name?: string
  provider?: string
  languages?: Array<{ code: string, title?: string }>
}

/** Official Kokoro Mandarin voices from hexgrad/Kokoro-82M VOICES.md. */
const KOKORO_MANDARIN_VOICE_IDS = [
  'zf_xiaobei',
  'zf_xiaoni',
  'zf_xiaoxiao',
  'zf_xiaoyi',
  'zm_yunjian',
  'zm_yunxi',
  'zm_yunxia',
  'zm_yunyang',
] as const

export interface ApplyXiaomiaoBridgeReactionParams {
  currentTimestamp: number
  currentText: string
  bridgeState: XiaomiaoBridgeState
  postCaption: (text: string) => void
  syncChatHistory: (text: string, createdAtMs: number) => void
  ensureSpeechReady?: () => Promise<void>
  speakReply: (text: string) => Promise<void>
}

export interface ApplyXiaomiaoBridgeReactionResult {
  accepted: boolean
  nextTimestamp: number
  nextText: string
}

export interface XiaomiaoStageActionEvent {
  id: number
  content: string
  event_type?: string
  result_summary?: string
  timestamp?: number
}

export type XiaomiaoStageActionName = 'say' | 'tts' | 'subtitle' | 'emotion' | 'background' | 'model' | 'status'

export interface XiaomiaoStageAction {
  id: number
  action: XiaomiaoStageActionName
  text?: string
  emotionName?: string
  intensity?: number
  backgroundId?: string
  modelId?: string
  query?: string
  createdAtMs: number
}

export interface XiaomiaoStageActionRejection {
  id: number
  action?: string
  reason: string
}

export interface ApplyXiaomiaoStageActionEventsParams {
  events: XiaomiaoStageActionEvent[]
  handledEventIds: Set<number>
  postCaption: (text: string) => void
  ensureSpeechReady?: () => Promise<void>
  speakReply: (text: string) => Promise<void>
  applyEmotion?: (name: string, intensity: number) => Promise<void>
  applyBackground?: (id: string) => Promise<void>
  applyModel?: (id: string) => Promise<void>
  readStatus?: (query?: string) => string | Promise<string>
  onRejected?: (rejection: XiaomiaoStageActionRejection) => void
}

export interface ApplyXiaomiaoStageActionEventsResult {
  accepted: XiaomiaoStageAction[]
  rejected: XiaomiaoStageActionRejection[]
}

export interface EnsureBridgeSpeechReadyParams {
  currentProvider: string
  currentModel: string
  currentVoiceId: string
  providerConfigModel?: string
  loadVoices: () => Promise<BridgeSpeechVoice[]>
  applyConfig: (config: { providerId: 'kokoro-local', modelId: string, voice: BridgeSpeechVoice }) => void
}

/**
 * Ensures the desktop bridge has a local speech provider that can drive lip sync.
 */
export async function ensureBridgeSpeechReady(params: EnsureBridgeSpeechReadyParams): Promise<boolean> {
  if (params.currentProvider !== 'speech-noop' && params.currentModel && params.currentVoiceId) {
    return false
  }

  const voices = await params.loadVoices()
  const voice = voices.find(candidate => KOKORO_MANDARIN_VOICE_IDS.includes(candidate.id as typeof KOKORO_MANDARIN_VOICE_IDS[number]))
    ?? voices.find(candidate => candidate.languages?.some(language => language.code === 'zh-CN'))
    ?? voices.find(candidate => candidate.id === 'af_heart')
    ?? voices[0]

  if (!voice) {
    return false
  }

  params.applyConfig({
    providerId: 'kokoro-local',
    modelId: params.providerConfigModel || 'q4f16',
    voice,
  })

  return true
}

/**
 * Applies a fresh XiaoMiao bridge reply to every desktop reaction surface.
 *
 * Use when:
 * - polling the local QQ bridge from the desktop renderer
 * - the same reply must drive caption, chat history, and TTS/lip-sync together
 *
 * Expects:
 * - `bridgeState` is already normalized by {@link readXiaomiaoBridgeState}
 * - handlers are idempotent because duplicate bridge payloads are filtered here
 *
 * Returns:
 * - the accepted/rejected state together with the next dedupe cursor
 */
export async function applyXiaomiaoBridgeReaction(
  params: ApplyXiaomiaoBridgeReactionParams,
): Promise<ApplyXiaomiaoBridgeReactionResult> {
  if (!shouldAdoptXiaomiaoBridgeState(
    params.currentTimestamp,
    params.bridgeState.timestamp,
    params.currentText,
    params.bridgeState.replyText,
  )) {
    return {
      accepted: false,
      nextTimestamp: params.currentTimestamp,
      nextText: params.currentText,
    }
  }

  params.postCaption(params.bridgeState.replyText)
  params.syncChatHistory(params.bridgeState.replyText, params.bridgeState.timestamp * 1000)
  await params.ensureSpeechReady?.()
  await params.speakReply(params.bridgeState.replyText)

  return {
    accepted: true,
    nextTimestamp: params.bridgeState.timestamp,
    nextText: params.bridgeState.replyText,
  }
}

export function parseXiaomiaoStageActionEvent(
  event: XiaomiaoStageActionEvent,
): XiaomiaoStageAction | null {
  if (event.event_type !== 'stage_action')
    return null

  const payloadAction = parseQueuedStageAction(event)
  if (payloadAction)
    return payloadAction

  const action = normalizeStageAction(event.result_summary)
  if (action) {
    const actionFromContent = buildStageActionFromText(event, action, event.content)
    if (!actionFromContent)
      return null
    return actionFromContent
  }

  return null
}

export async function applyXiaomiaoStageActionEvents(
  params: ApplyXiaomiaoStageActionEventsParams,
): Promise<ApplyXiaomiaoStageActionEventsResult> {
  const accepted: XiaomiaoStageAction[] = []
  const rejected: XiaomiaoStageActionRejection[] = []

  for (const event of params.events) {
    if (params.handledEventIds.has(event.id))
      continue

    const action = parseXiaomiaoStageActionEvent(event)
    if (!action) {
      if (event.event_type === 'stage_action') {
        const rejection = rejectEvent(event, '无法解析或不支持的舞台动作')
        params.handledEventIds.add(event.id)
        rejected.push(rejection)
        params.onRejected?.(rejection)
      }
      continue
    }

    params.handledEventIds.add(event.id)
    const rejection = await applyStageAction(params, action)
    if (rejection) {
      rejected.push(rejection)
      params.onRejected?.(rejection)
    }
    else {
      accepted.push(action)
    }
  }

  return { accepted, rejected }
}

function buildStageAction(
  event: XiaomiaoStageActionEvent,
  action: XiaomiaoStageActionName,
  payload: Omit<XiaomiaoStageAction, 'id' | 'action' | 'createdAtMs'> = {},
): XiaomiaoStageAction {
  return {
    id: event.id,
    action,
    createdAtMs: (event.timestamp ?? 0) * 1000,
    ...payload,
  }
}

function buildStageActionFromText(
  event: XiaomiaoStageActionEvent,
  action: XiaomiaoStageActionName,
  content: string,
): XiaomiaoStageAction | null {
  const text = content.trim()
  if (!text && action !== 'status')
    return null

  if (action === 'say' || action === 'tts' || action === 'subtitle')
    return buildStageAction(event, action, { text })
  if (action === 'emotion')
    return buildStageAction(event, action, { emotionName: text, intensity: 1 })
  if (action === 'background')
    return buildStageAction(event, action, { backgroundId: text })
  if (action === 'model')
    return buildStageAction(event, action, { modelId: text })
  if (action === 'status')
    return buildStageAction(event, action, { query: text || 'current' })

  return null
}

function normalizeStageAction(value: string | undefined): XiaomiaoStageActionName | null {
  const normalized = value?.trim().toLowerCase()
  if (!normalized)
    return null

  const action = normalized.includes(':')
    ? normalized.split(':').at(-1)
    : normalized

  if (
    action === 'say'
    || action === 'tts'
    || action === 'subtitle'
    || action === 'emotion'
    || action === 'background'
    || action === 'model'
    || action === 'status'
  ) {
    return action
  }

  return null
}

function parseQueuedStageAction(event: XiaomiaoStageActionEvent): XiaomiaoStageAction | null {
  let parsed: unknown
  try {
    parsed = JSON.parse(event.content)
  }
  catch {
    return null
  }

  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed))
    return null

  const record = parsed as Record<string, unknown>
  if (record.service !== 'stage')
    return null

  const action = typeof record.action === 'string'
    ? normalizeStageAction(record.action)
    : null
  if (!action)
    return null

  const payload = record.payload
  if (!payload || typeof payload !== 'object' || Array.isArray(payload))
    return null

  return buildStageActionFromPayload(event, action, payload as Record<string, unknown>)
}

function buildStageActionFromPayload(
  event: XiaomiaoStageActionEvent,
  action: XiaomiaoStageActionName,
  payload: Record<string, unknown>,
): XiaomiaoStageAction | null {
  if (action === 'say' || action === 'tts' || action === 'subtitle') {
    const text = firstPayloadText(payload)
    if (!text)
      return null
    return buildStageAction(event, action, { text })
  }

  if (action === 'emotion') {
    const name = firstPayloadString(payload, ['name', 'emotion', 'emotionName', 'id'])
    if (!name)
      return null
    return buildStageAction(event, action, {
      emotionName: name,
      intensity: normalizeIntensity(payload.intensity),
    })
  }

  if (action === 'background') {
    const id = firstPayloadString(payload, ['id', 'backgroundId', 'name'])
    if (!id)
      return null
    return buildStageAction(event, action, { backgroundId: id })
  }

  if (action === 'model') {
    const id = firstPayloadString(payload, ['id', 'modelId', 'displayModelId', 'name'])
    if (!id)
      return null
    return buildStageAction(event, action, { modelId: id })
  }

  if (action === 'status') {
    const query = firstPayloadString(payload, ['query', 'scope', 'text']) ?? 'current'
    return buildStageAction(event, action, { query })
  }

  return null
}

async function applyStageAction(
  params: ApplyXiaomiaoStageActionEventsParams,
  action: XiaomiaoStageAction,
): Promise<XiaomiaoStageActionRejection | null> {
  try {
    if (action.action === 'say' || action.action === 'tts') {
      if (!action.text)
        return reject(action, '缺少播报文本')
      params.postCaption(action.text)
      await params.ensureSpeechReady?.()
      await params.speakReply(action.text)
      return null
    }

    if (action.action === 'subtitle') {
      if (!action.text)
        return reject(action, '缺少字幕文本')
      params.postCaption(action.text)
      return null
    }

    if (action.action === 'emotion') {
      if (!action.emotionName)
        return reject(action, '缺少表情名称')
      if (params.applyEmotion) {
        await params.applyEmotion(action.emotionName, action.intensity ?? 1)
      }
      else {
        await params.speakReply(formatEmotionToken(action.emotionName, action.intensity ?? 1))
      }
      return null
    }

    if (action.action === 'background') {
      if (!action.backgroundId)
        return reject(action, '缺少背景 ID')
      if (!params.applyBackground)
        return reject(action, '当前舞台未注册背景切换处理器')
      await params.applyBackground(action.backgroundId)
      params.postCaption(`背景已切换：${action.backgroundId}`)
      return null
    }

    if (action.action === 'model') {
      if (!action.modelId)
        return reject(action, '缺少模型 ID')
      if (!params.applyModel)
        return reject(action, '当前舞台未注册模型切换处理器')
      await params.applyModel(action.modelId)
      params.postCaption(`模型已切换：${action.modelId}`)
      return null
    }

    if (action.action === 'status') {
      if (!params.readStatus)
        return reject(action, '当前舞台未注册状态读取处理器')
      const status = await params.readStatus(action.query)
      params.postCaption(status)
      return null
    }

    return reject(action, '不支持的舞台动作')
  }
  catch (error) {
    return reject(action, error instanceof Error ? error.message : String(error))
  }
}

function reject(action: XiaomiaoStageAction, reason: string): XiaomiaoStageActionRejection {
  return {
    id: action.id,
    action: action.action,
    reason,
  }
}

function rejectEvent(event: XiaomiaoStageActionEvent, reason: string): XiaomiaoStageActionRejection {
  return {
    id: event.id,
    action: rawStageActionName(event),
    reason,
  }
}

function rawStageActionName(event: XiaomiaoStageActionEvent): string | undefined {
  const summary = event.result_summary?.trim()
  if (summary)
    return summary.includes(':') ? summary.split(':').at(-1) : summary

  try {
    const parsed = JSON.parse(event.content) as unknown
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed))
      return undefined
    const action = (parsed as Record<string, unknown>).action
    return typeof action === 'string' && action.trim() ? action.trim() : undefined
  }
  catch {
    return undefined
  }
}

function firstPayloadString(payload: Record<string, unknown>, keys: string[]): string | null {
  for (const key of keys) {
    const value = payload[key]
    if (typeof value !== 'string')
      continue
    const text = value.trim()
    if (text)
      return text
  }

  return null
}

function normalizeIntensity(value: unknown): number {
  if (typeof value !== 'number' || !Number.isFinite(value))
    return 1
  return Math.max(0, Math.min(value, 1))
}

function formatEmotionToken(name: string, intensity: number): string {
  return `<|ACT ${JSON.stringify({ emotion: { name, intensity } })}|>`
}

function firstPayloadText(payload: Record<string, unknown>): string | null {
  const text = firstPayloadString(payload, ['text', 'content', 'message', 'subtitle', 'speech'])
  if (!text)
    return null

  return text
}
