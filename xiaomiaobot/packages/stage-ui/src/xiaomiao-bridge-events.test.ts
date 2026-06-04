import type { ChatHistoryItem } from './types/chat'
import { describe, expect, it } from 'vitest'
import {
  appendXiaomiaoBridgeEvents,
  requestXiaomiaoBridgeConfigStatus,
  requestXiaomiaoBridgeEvents,
  saveXiaomiaoBridgeConfig,
} from '../../stage-layouts/src/xiaomiao-bridge'

describe('xiaomiao bridge events', () => {
  it('requests bridge events with cursor and user filter', async () => {
    const calls: string[] = []
    const result = await requestXiaomiaoBridgeEvents({
      after: 7,
      userId: 42,
      fetcher: async (input) => {
        calls.push(String(input))
        return jsonResponse({
          last_id: 8,
          events: [{
            id: 8,
            source: 'qq-private',
            channel: 'qq-private',
            chat_id: '42',
            user_id: 42,
            role: 'user',
            content: '你好',
            timestamp: 1780399500,
          }],
        })
      },
    })

    expect(calls[0]).toContain('/v1/xiaomiao/events?after=7&user_id=42')
    expect(result.lastId).toBe(8)
    expect(result.events[0].content).toBe('你好')
  })

  it('appends non-web events and skips duplicates', () => {
    const messages: ChatHistoryItem[] = [{
      id: 'xiaomiao-event-1',
      role: 'user',
      content: '已有消息',
    }]

    const next = appendXiaomiaoBridgeEvents(messages, [
      bridgeEvent(1, 'qq-private', 'user', '重复消息'),
      bridgeEvent(2, 'web', 'user', '本地网页消息'),
      bridgeEvent(3, 'qq-group', 'user', '群里问'),
      bridgeEvent(4, 'qq-group', 'assistant', '群里答'),
    ])

    expect(next).toHaveLength(3)
    expect(next[1].id).toBe('xiaomiao-event-3')
    expect(next[1].content).toBe('[QQ群 42] 群里问')
    expect(next[2].role).toBe('assistant')
    expect(next[2].content).toBe('[QQ群 42] 群里答')
  })

  it('requests bridge root config status without requiring secrets', async () => {
    const calls: string[] = []
    const result = await requestXiaomiaoBridgeConfigStatus({
      fetcher: async (input) => {
        calls.push(String(input))
        return jsonResponse({
          configured: true,
          provider: 'custom',
          model: 'deepseek-v4-flash',
          baseUrl: 'https://relay.example.com/v1',
          hasApiKey: true,
        })
      },
    })

    expect(calls[0]).toContain('/v1/xiaomiao/config')
    expect(result).toEqual({
      configured: true,
      provider: 'custom',
      model: 'deepseek-v4-flash',
      baseUrl: 'https://relay.example.com/v1',
      hasApiKey: true,
    })
  })

  it('saves bridge root config through the local config route', async () => {
    const bodies: unknown[] = []
    const result = await saveXiaomiaoBridgeConfig({
      apiKey: 'secret-key',
      baseUrl: 'https://relay.example.com/v1',
      model: 'deepseek-v4-flash',
      fetcher: async (_input, init) => {
        bodies.push(JSON.parse(String(init?.body)))
        return jsonResponse({
          configured: true,
          provider: 'custom',
          model: 'deepseek-v4-flash',
          baseUrl: 'https://relay.example.com/v1',
          hasApiKey: true,
        })
      },
    })

    expect(bodies[0]).toEqual({
      apiKey: 'secret-key',
      baseUrl: 'https://relay.example.com/v1',
      model: 'deepseek-v4-flash',
    })
    expect(result.configured).toBe(true)
  })
})

function bridgeEvent(id: number, source: string, role: 'user' | 'assistant', content: string) {
  return {
    id,
    source,
    channel: source,
    chat_id: '42',
    user_id: 42,
    role,
    content,
    timestamp: 1780399500 + id,
  }
}

function jsonResponse(payload: unknown) {
  return {
    ok: true,
    status: 200,
    json: async () => payload,
  } as Response
}
