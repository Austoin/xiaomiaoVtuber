import { afterEach, describe, expect, it, vi } from 'vitest'

import { LLMAgent } from './llm-agent'

describe('lLMAgent', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('routes Minecraft reasoning through the unified xiaomiaoAgent API', async () => {
    const fetchMock = vi.fn(async (_input: unknown, _init?: RequestInit) => new Response(JSON.stringify({
      choices: [{ message: { content: '{"actions":[]}' } }],
      usage: { prompt_tokens: 10, completion_tokens: 4, total_tokens: 14 },
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }))
    vi.stubGlobal('fetch', fetchMock)
    const agent = new LLMAgent({
      apiUrl: 'http://127.0.0.1:8900/v1/chat/completions',
      sessionId: 'minecraft-runtime',
    })

    const result = await agent.callLLM({
      messages: [{ role: 'user', content: 'Plan the next action.' }],
      responseFormat: { type: 'json_object' },
    })

    expect(result.text).toBe('{"actions":[]}')
    expect(result.usage.total_tokens).toBe(14)
    expect(fetchMock).toHaveBeenCalledOnce()
    const [url, init] = fetchMock.mock.calls[0]!
    expect(url).toBe('http://127.0.0.1:8900/v1/chat/completions')
    const body = JSON.parse(String(init?.body))
    expect(body).toMatchObject({
      session_id: 'minecraft-runtime',
      channel: 'minecraft',
      chat_id: 'minecraft-bot',
      user_id: 'minecraft-bot',
    })
    expect(body.messages).toEqual([{ role: 'user', content: 'Plan the next action.' }])
    expect(body).not.toHaveProperty('model')
    expect(body).not.toHaveProperty('apiKey')
  })

  it('exposes an Agent HTTP failure instead of falling back to another model', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('upstream unavailable', { status: 502 })))
    const agent = new LLMAgent({
      apiUrl: 'http://127.0.0.1:8900/v1/chat/completions',
      sessionId: 'minecraft-runtime',
    })

    await expect(agent.callLLM({
      messages: [{ role: 'user', content: 'Move.' }],
    })).rejects.toThrow('xiaomiaoAgent request failed with HTTP 502: upstream unavailable')
  })
})
