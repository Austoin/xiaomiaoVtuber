import type { ChatHistoryItem } from '@proj-airi/stage-ui/types/chat'

const XIAOMIAO_BRIDGE_BASE_URL = 'http://127.0.0.1:5519'
const DEFAULT_XIAOMIAO_MODEL = 'deepseek-chat'

export interface XiaomiaoBridgeRequest {
  text: string
  model?: string | null
  fetcher?: typeof globalThis.fetch
}

export interface XiaomiaoBridgeEvent {
  id: number
  source: string
  channel: string
  chat_id: string
  user_id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

export interface XiaomiaoBridgeEventsRequest {
  after?: number
  userId?: number
  fetcher?: typeof globalThis.fetch
}

export interface XiaomiaoBridgeEventsResult {
  events: XiaomiaoBridgeEvent[]
  lastId: number
}

export interface XiaomiaoBridgeConfigStatus {
  configured: boolean
  provider: string
  model: string
  baseUrl: string
  hasApiKey: boolean
}

export interface XiaomiaoBridgeConfigRequest {
  fetcher?: typeof globalThis.fetch
}

export interface XiaomiaoBridgeConfigUpdate {
  apiKey: string
  baseUrl: string
  model: string
  fetcher?: typeof globalThis.fetch
}

interface XiaomiaoBridgeResponse {
  choices?: Array<{
    message?: {
      content?: string
    }
  }>
}

interface XiaomiaoBridgeEventsResponse {
  events?: unknown
  last_id?: unknown
}

interface XiaomiaoBridgeConfigResponse {
  configured?: unknown
  provider?: unknown
  model?: unknown
  baseUrl?: unknown
  hasApiKey?: unknown
}

export async function requestXiaomiaoBridgeReply(params: XiaomiaoBridgeRequest): Promise<string> {
  const fetcher = params.fetcher ?? globalThis.fetch
  if (typeof fetcher !== 'function') {
    throw new Error('XiaoMiao bridge requires fetch support')
  }

  const response = await fetcher(`${XIAOMIAO_BRIDGE_BASE_URL}/v1/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: params.model?.trim() || DEFAULT_XIAOMIAO_MODEL,
      messages: [{ role: 'user', content: params.text }],
    }),
  })

  if (!response.ok) {
    throw new Error(`XiaoMiao bridge request failed with HTTP ${response.status}`)
  }

  const data = await response.json() as XiaomiaoBridgeResponse
  const replyText = data.choices?.[0]?.message?.content?.trim()
  if (!replyText) {
    throw new Error('XiaoMiao bridge returned an empty reply')
  }

  return replyText
}

export async function requestXiaomiaoBridgeConfigStatus(params: XiaomiaoBridgeConfigRequest = {}): Promise<XiaomiaoBridgeConfigStatus> {
  const fetcher = params.fetcher ?? globalThis.fetch
  if (typeof fetcher !== 'function') {
    throw new Error('XiaoMiao bridge config requires fetch support')
  }

  const response = await fetcher(`${XIAOMIAO_BRIDGE_BASE_URL}/v1/xiaomiao/config`)
  if (!response.ok) {
    throw new Error(`XiaoMiao bridge config request failed with HTTP ${response.status}`)
  }

  const data = await response.json() as XiaomiaoBridgeConfigResponse
  return normalizeXiaomiaoBridgeConfigStatus(data)
}

export async function saveXiaomiaoBridgeConfig(params: XiaomiaoBridgeConfigUpdate): Promise<XiaomiaoBridgeConfigStatus> {
  const fetcher = params.fetcher ?? globalThis.fetch
  if (typeof fetcher !== 'function') {
    throw new Error('XiaoMiao bridge config save requires fetch support')
  }

  const response = await fetcher(`${XIAOMIAO_BRIDGE_BASE_URL}/v1/xiaomiao/config`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      apiKey: params.apiKey,
      baseUrl: params.baseUrl,
      model: params.model,
    }),
  })

  if (!response.ok) {
    throw new Error(`XiaoMiao bridge config save failed with HTTP ${response.status}`)
  }

  const data = await response.json() as XiaomiaoBridgeConfigResponse
  return normalizeXiaomiaoBridgeConfigStatus(data)
}

export async function requestXiaomiaoBridgeEvents(params: XiaomiaoBridgeEventsRequest = {}): Promise<XiaomiaoBridgeEventsResult> {
  const fetcher = params.fetcher ?? globalThis.fetch
  if (typeof fetcher !== 'function') {
    throw new Error('XiaoMiao bridge events require fetch support')
  }

  const url = new URL(`${XIAOMIAO_BRIDGE_BASE_URL}/v1/xiaomiao/events`)
  url.searchParams.set('after', String(params.after ?? 0))
  if (params.userId !== undefined)
    url.searchParams.set('user_id', String(params.userId))

  const response = await fetcher(url.toString())
  if (!response.ok) {
    throw new Error(`XiaoMiao bridge events request failed with HTTP ${response.status}`)
  }

  const data = await response.json() as XiaomiaoBridgeEventsResponse
  if (!Array.isArray(data.events)) {
    throw new Error('XiaoMiao bridge events response is missing events')
  }
  if (typeof data.last_id !== 'number') {
    throw new Error('XiaoMiao bridge events response is missing last_id')
  }

  return {
    events: data.events.map(normalizeXiaomiaoBridgeEvent),
    lastId: data.last_id,
  }
}

export function appendXiaomiaoBridgeExchange(
  messages: ChatHistoryItem[],
  userText: string,
  replyText: string,
): ChatHistoryItem[] {
  const createdAt = Date.now()
  return [
    ...messages,
    {
      id: `xiaomiao-user-${createdAt.toString(36)}`,
      role: 'user',
      content: userText,
      createdAt,
    },
    {
      id: `xiaomiao-assistant-${createdAt.toString(36)}`,
      role: 'assistant',
      content: replyText,
      slices: [],
      tool_results: [],
      createdAt,
    },
  ]
}

export function appendXiaomiaoBridgeEvents(
  messages: ChatHistoryItem[],
  events: XiaomiaoBridgeEvent[],
  options: { includeWeb?: boolean } = {},
): ChatHistoryItem[] {
  const existingIds = new Set(messages.map(message => message.id).filter(Boolean))
  const nextMessages = [...messages]

  for (const event of events) {
    if (!options.includeWeb && event.source === 'web')
      continue

    const id = `xiaomiao-event-${event.id}`
    if (existingIds.has(id))
      continue

    nextMessages.push(toChatHistoryItem(event, id))
    existingIds.add(id)
  }

  return nextMessages.length === messages.length ? messages : nextMessages
}

export function appendXiaomiaoBridgeError(
  messages: ChatHistoryItem[],
  userText: string,
  errorText: string,
): ChatHistoryItem[] {
  return [
    ...messages,
    {
      id: `xiaomiao-error-user-${Date.now().toString(36)}`,
      role: 'user',
      content: userText,
      createdAt: Date.now(),
    },
    {
      role: 'error',
      content: errorText,
    },
  ]
}

function normalizeXiaomiaoBridgeConfigStatus(value: XiaomiaoBridgeConfigResponse): XiaomiaoBridgeConfigStatus {
  return {
    configured: requireBoolean(value.configured, 'configured'),
    provider: requireString(value.provider, 'provider'),
    model: requireString(value.model, 'model'),
    baseUrl: requireString(value.baseUrl, 'baseUrl'),
    hasApiKey: requireBoolean(value.hasApiKey, 'hasApiKey'),
  }
}

function normalizeXiaomiaoBridgeEvent(value: unknown): XiaomiaoBridgeEvent {
  if (!value || typeof value !== 'object') {
    throw new Error('XiaoMiao bridge event must be an object')
  }

  const raw = value as Record<string, unknown>
  if (raw.role !== 'user' && raw.role !== 'assistant') {
    throw new Error('XiaoMiao bridge event role must be user or assistant')
  }

  return {
    id: requireNumber(raw.id, 'id'),
    source: requireString(raw.source, 'source'),
    channel: requireString(raw.channel, 'channel'),
    chat_id: requireString(raw.chat_id, 'chat_id'),
    user_id: requireNumber(raw.user_id, 'user_id'),
    role: raw.role,
    content: requireString(raw.content, 'content'),
    timestamp: requireNumber(raw.timestamp, 'timestamp'),
  }
}

function toChatHistoryItem(event: XiaomiaoBridgeEvent, id: string): ChatHistoryItem {
  if (event.role === 'assistant') {
    return {
      id,
      role: 'assistant',
      content: formatBridgeEventContent(event),
      slices: [],
      tool_results: [],
      createdAt: event.timestamp * 1000,
    }
  }

  return {
    id,
    role: 'user',
    content: formatBridgeEventContent(event),
    createdAt: event.timestamp * 1000,
  }
}

function formatBridgeEventContent(event: XiaomiaoBridgeEvent): string {
  if (event.source === 'web')
    return event.content

  return `[${formatBridgeEventSource(event)}] ${event.content}`
}

function formatBridgeEventSource(event: XiaomiaoBridgeEvent): string {
  if (event.source === 'qq-group')
    return `QQ群 ${event.chat_id}`
  if (event.source === 'qq-private')
    return `QQ私聊 ${event.chat_id}`
  return event.source
}

function requireNumber(value: unknown, name: string): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`XiaoMiao bridge event ${name} must be a number`)
  }
  return value
}

function requireString(value: unknown, name: string): string {
  if (typeof value !== 'string') {
    throw new Error(`XiaoMiao bridge event ${name} must be a string`)
  }
  return value
}

function requireBoolean(value: unknown, name: string): boolean {
  if (typeof value !== 'boolean') {
    throw new Error(`XiaoMiao bridge config ${name} must be a boolean`)
  }
  return value
}
