import { afterEach, describe, expect, it, vi } from 'vitest'

import { requestXiaomiaoAgentReply } from './xiaomiao-agent'

function jsonResponse(body: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
}

describe('xiaomiaoAgent HTTP client', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('posts the unified session envelope and returns the assistant text', async () => {
    const fetcher = vi.fn(async () => jsonResponse({
      choices: [{ message: { content: '  hello from agent  ' } }],
    }))

    const reply = await requestXiaomiaoAgentReply({
      text: 'hello',
      clientMessageId: ' message-1 ',
      fetcher,
    })

    expect(reply).toBe('hello from agent')
    expect(fetcher).toHaveBeenCalledWith(
      'http://127.0.0.1:8900/v1/chat/completions',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          session_id: 'xiaomiao-unified',
          channel: 'web',
          chat_id: 'stage-client',
          user_id: 'stage-client',
          client_message_id: 'message-1',
          messages: [{ role: 'user', content: 'hello' }],
        }),
      }),
    )
  })

  it('fails within the configured timeout', async () => {
    vi.useFakeTimers()
    const fetcher = vi.fn(() => new Promise<Response>((resolve) => {
      setTimeout(() => resolve(jsonResponse({
        choices: [{ message: { content: 'late reply' } }],
      })), 50)
    }))

    const request = requestXiaomiaoAgentReply({
      text: 'hello',
      timeoutMs: 10,
      fetcher: fetcher as typeof fetch,
    })
    const assertion = expect(request).rejects.toThrow('timed out after 10ms')

    await vi.advanceTimersByTimeAsync(50)
    await assertion
  })

  it('includes bounded backend detail in HTTP errors', async () => {
    const fetcher = vi.fn(async () => new Response('backend unavailable', { status: 503 }))

    await expect(requestXiaomiaoAgentReply({
      text: 'hello',
      fetcher,
    })).rejects.toThrow('HTTP 503: backend unavailable')
  })

  it('propagates caller cancellation to the active request', async () => {
    const controller = new AbortController()
    const requestSignals: AbortSignal[] = []
    const fetcher = vi.fn((_: RequestInfo | URL, init?: RequestInit) => {
      if (init?.signal)
        requestSignals.push(init.signal)
      return new Promise<Response>(() => {})
    }) as typeof fetch
    const request = requestXiaomiaoAgentReply({
      text: 'hello',
      signal: controller.signal,
      fetcher,
    })
    const assertion = expect(request).rejects.toThrow('cancelled by caller')
    await Promise.resolve()

    controller.abort(new Error('cancelled by caller'))

    await assertion
    expect(requestSignals[0]?.aborted).toBe(true)
  })

  it('rejects invalid timeout values before sending', async () => {
    const fetcher = vi.fn()

    await expect(requestXiaomiaoAgentReply({
      text: 'hello',
      timeoutMs: 0,
      fetcher,
    })).rejects.toThrow('timeoutMs must be a positive finite number')
    expect(fetcher).not.toHaveBeenCalled()
  })
})
