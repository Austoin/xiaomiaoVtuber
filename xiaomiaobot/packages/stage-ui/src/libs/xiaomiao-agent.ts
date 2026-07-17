const XIAOMIAO_AGENT_BASE_URL = 'http://127.0.0.1:8900'
const XIAOMIAO_AGENT_SESSION_ID = 'xiaomiao-unified'
const XIAOMIAO_STAGE_CHAT_ID = 'stage-client'
const DEFAULT_REQUEST_TIMEOUT_MS = 120_000
const MAX_ERROR_DETAIL_LENGTH = 500

export interface XiaomiaoAgentRequest {
  text: string
  media?: string[]
  clientMessageId?: string | null
  channel?: string
  chatId?: string
  userId?: string
  sessionId?: string
  signal?: AbortSignal
  timeoutMs?: number
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

  const timeoutMs = normalizeTimeoutMs(params.timeoutMs)
  const request = createCancellableRequest(params.signal, timeoutMs)

  try {
    const response = await Promise.race([
      Promise.resolve().then(() => fetcher(`${XIAOMIAO_AGENT_BASE_URL}/v1/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: request.signal,
        body: JSON.stringify({
          session_id: params.sessionId ?? XIAOMIAO_AGENT_SESSION_ID,
          channel: params.channel ?? 'web',
          chat_id: params.chatId ?? XIAOMIAO_STAGE_CHAT_ID,
          user_id: params.userId ?? XIAOMIAO_STAGE_CHAT_ID,
          ...(params.clientMessageId?.trim() ? { client_message_id: params.clientMessageId.trim() } : {}),
          messages: [{ role: 'user', content: buildAgentUserContent(params.text, params.media) }],
        }),
      })),
      request.cancelled,
    ])

    if (!response.ok) {
      const detail = await readErrorDetail(response)
      throw new Error(`xiaomiaoAgent request failed with HTTP ${response.status}${detail ? `: ${detail}` : ''}`)
    }

    const data = await response.json() as XiaomiaoAgentResponse
    const replyText = data.choices?.[0]?.message?.content?.trim()
    if (!replyText)
      throw new Error('xiaomiaoAgent returned an empty reply')

    return replyText
  }
  finally {
    request.dispose()
  }
}

function normalizeTimeoutMs(value?: number) {
  const timeoutMs = value ?? DEFAULT_REQUEST_TIMEOUT_MS
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0)
    throw new RangeError('xiaomiaoAgent timeoutMs must be a positive finite number')
  return Math.floor(timeoutMs)
}

function createCancellableRequest(parentSignal: AbortSignal | undefined, timeoutMs: number) {
  if (parentSignal?.aborted)
    throw abortReason(parentSignal)

  const controller = new AbortController()
  let rejectCancellation: (reason: Error) => void = () => {}
  let settled = false
  const cancelled = new Promise<never>((_, reject) => {
    rejectCancellation = reject
  })

  function cancel(reason: Error) {
    if (settled)
      return
    rejectCancellation(reason)
    controller.abort(reason)
  }

  const timeout = setTimeout(() => {
    cancel(new Error(`xiaomiaoAgent request timed out after ${timeoutMs}ms`))
  }, timeoutMs)
  const onParentAbort = () => cancel(abortReason(parentSignal!))
  parentSignal?.addEventListener('abort', onParentAbort, { once: true })

  return {
    signal: controller.signal,
    cancelled,
    dispose() {
      settled = true
      clearTimeout(timeout)
      parentSignal?.removeEventListener('abort', onParentAbort)
    },
  }
}

function abortReason(signal: AbortSignal) {
  return signal.reason instanceof Error
    ? signal.reason
    : new Error('xiaomiaoAgent request was aborted')
}

async function readErrorDetail(response: Response) {
  try {
    return (await response.text()).trim().slice(0, MAX_ERROR_DETAIL_LENGTH)
  }
  catch {
    return ''
  }
}

function buildAgentUserContent(text: string, media?: string[]) {
  if (!media?.length)
    return text

  return [
    { type: 'text', text },
    ...media.map(url => ({ type: 'image_url', image_url: { url } })),
  ]
}
