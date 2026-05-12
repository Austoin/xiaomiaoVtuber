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
