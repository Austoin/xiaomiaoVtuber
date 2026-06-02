import type { ChatHistoryItem } from '@proj-airi/stage-ui/types/chat'

const XIAOMIAO_BRIDGE_BASE_URL = 'http://127.0.0.1:5519'
const DEFAULT_XIAOMIAO_MODEL = 'deepseek-chat'

export interface XiaomiaoBridgeRequest {
  text: string
  model?: string | null
  fetcher?: typeof globalThis.fetch
}

interface XiaomiaoBridgeResponse {
  choices?: Array<{
    message?: {
      content?: string
    }
  }>
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
