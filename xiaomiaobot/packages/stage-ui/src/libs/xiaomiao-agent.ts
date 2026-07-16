const XIAOMIAO_AGENT_BASE_URL = 'http://127.0.0.1:8900'
const XIAOMIAO_AGENT_SESSION_ID = 'xiaomiao-unified'
const XIAOMIAO_STAGE_CHAT_ID = 'stage-client'

export interface XiaomiaoAgentRequest {
  text: string
  media?: string[]
  clientMessageId?: string | null
  channel?: string
  chatId?: string
  userId?: string
  sessionId?: string
  signal?: AbortSignal
  fetcher?: typeof globalThis.fetch
}

interface XiaomiaoAgentResponse {
  choices?: Array<{
    message?: {
      content?: string
    }
  }>
}

export async function requestXiaomiaoAgentReply(params: XiaomiaoAgentRequest): Promise<string> {
  const fetcher = params.fetcher ?? globalThis.fetch
  if (typeof fetcher !== 'function')
    throw new TypeError('xiaomiaoAgent requires fetch support')

  const response = await fetcher(`${XIAOMIAO_AGENT_BASE_URL}/v1/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    signal: params.signal,
    body: JSON.stringify({
      session_id: params.sessionId ?? XIAOMIAO_AGENT_SESSION_ID,
      channel: params.channel ?? 'web',
      chat_id: params.chatId ?? XIAOMIAO_STAGE_CHAT_ID,
      user_id: params.userId ?? XIAOMIAO_STAGE_CHAT_ID,
      ...(params.clientMessageId?.trim() ? { client_message_id: params.clientMessageId.trim() } : {}),
      messages: [{ role: 'user', content: buildAgentUserContent(params.text, params.media) }],
    }),
  })

  if (!response.ok)
    throw new Error(`xiaomiaoAgent request failed with HTTP ${response.status}`)

  const data = await response.json() as XiaomiaoAgentResponse
  const replyText = data.choices?.[0]?.message?.content?.trim()
  if (!replyText)
    throw new Error('xiaomiaoAgent returned an empty reply')

  return replyText
}

function buildAgentUserContent(text: string, media?: string[]) {
  if (!media?.length)
    return text

  return [
    { type: 'text', text },
    ...media.map(url => ({ type: 'image_url', image_url: { url } })),
  ]
}
