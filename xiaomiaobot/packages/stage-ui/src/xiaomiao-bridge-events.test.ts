import type { ChatHistoryItem } from './types/chat'

import { describe, expect, it, vi } from 'vitest'

import {
  appendXiaomiaoBridgeEvents,
  appendXiaomiaoBridgeExchange,
  appendXiaomiaoBridgeReply,
  createXiaomiaoBridgeEventSync,
  requestXiaomiaoBridgeConfigStatus,
  requestXiaomiaoBridgeEvents,
  requestXiaomiaoBridgeReply,
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
            client_message_id: 'stage-web-local-1',
            event_type: 'confirmation_requested',
            risk_level: 'high',
            confirmation_id: 'ABC123',
            result_summary: '等待确认',
          }],
        })
      },
    })

    expect(calls[0]).toBe('http://127.0.0.1:8900/v1/xiaomiao/events?after=7&user_id=42')
    expect(result.lastId).toBe(8)
    expect(result.events[0].content).toBe('你好')
    expect(result.events[0].client_message_id).toBe('stage-web-local-1')
    expect(result.events[0].schema_version).toBe(1)
    expect(result.events[0].conversation_id).toBe('qq-private:42')
    expect(result.events[0].message_id).toBe('client:stage-web-local-1:user')
    expect(result.events[0].event_type).toBe('confirmation_requested')
    expect(result.events[0].risk_level).toBe('high')
    expect(result.events[0].confirmation_id).toBe('ABC123')
    expect(result.events[0].result_summary).toBe('等待确认')
  })

  it('sends client message id with chat completion requests', async () => {
    const bodies: unknown[] = []
    const reply = await requestXiaomiaoBridgeReply({
      text: '你好',
      clientMessageId: 'stage-web-local-2',
      fetcher: async (_input, init) => {
        bodies.push(JSON.parse(String(init?.body)))
        return jsonResponse({
          choices: [{ message: { content: '你好呀' } }],
        })
      },
    })

    expect(reply).toBe('你好呀')
    expect(bodies[0]).toEqual({
      session_id: 'xiaomiao-unified',
      channel: 'web',
      chat_id: 'stage-client',
      user_id: 'stage-client',
      client_message_id: 'stage-web-local-2',
      messages: [{ role: 'user', content: '你好' }],
    })
  })

  it('requests and appends bridge replies through the shared helper', async () => {
    const bodies: unknown[] = []
    const next = await appendXiaomiaoBridgeReply([], {
      text: '语音问题',
      clientMessageId: 'stage-web-voice-1',
      fetcher: async (_input, init) => {
        bodies.push(JSON.parse(String(init?.body)))
        return jsonResponse({
          choices: [{ message: { content: '语音回答' } }],
        })
      },
    })

    expect(bodies[0]).toEqual({
      session_id: 'xiaomiao-unified',
      channel: 'web',
      chat_id: 'stage-client',
      user_id: 'stage-client',
      client_message_id: 'stage-web-voice-1',
      messages: [{ role: 'user', content: '语音问题' }],
    })
    expect(next).toHaveLength(2)
    expect(next[0].id).toBe('xiaomiao-client-stage-web-voice-1-user')
    expect(next[1].id).toBe('xiaomiao-client-stage-web-voice-1-assistant')
    expect(next[1].content).toBe('语音回答')
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

  it('uses client message id to avoid replaying confirmed local web events', () => {
    const messages = appendXiaomiaoBridgeExchange(
      [],
      '本地问题',
      '本地回答',
      { clientMessageId: 'stage-web-local-3' },
    )

    const next = appendXiaomiaoBridgeEvents(
      messages,
      [
        bridgeEvent(5, 'web', 'user', '本地问题', 'stage-web-local-3'),
        bridgeEvent(6, 'web', 'assistant', '本地回答', 'stage-web-local-3'),
      ],
      { includeWeb: true },
    )

    expect(next).toHaveLength(2)
    expect(next[0].id).toBe('xiaomiao-client-stage-web-local-3-user')
    expect(next[1].id).toBe('xiaomiao-client-stage-web-local-3-assistant')
  })

  it('can replay web events from bridge when local history is empty', () => {
    const next = appendXiaomiaoBridgeEvents(
      [],
      [
        bridgeEvent(7, 'web', 'user', '刷新前的问题', 'stage-web-local-4'),
        bridgeEvent(8, 'web', 'assistant', '刷新前的回答', 'stage-web-local-4'),
      ],
      { includeWeb: true },
    )

    expect(next).toHaveLength(2)
    expect(next[0].id).toBe('xiaomiao-client-stage-web-local-4-user')
    expect(next[0].content).toBe('刷新前的问题')
    expect(next[1].id).toBe('xiaomiao-client-stage-web-local-4-assistant')
    expect(next[1].content).toBe('刷新前的回答')
  })

  it('formats confirmation and tool events without duplicating messages', () => {
    const next = appendXiaomiaoBridgeEvents(
      [],
      [
        bridgeEvent(9, 'qq-group', 'assistant', '需要确认高风险动作', undefined, {
          event_type: 'confirmation_requested',
          risk_level: 'high',
          confirmation_id: 'ABC123',
        }),
        bridgeEvent(10, 'qq-group', 'assistant', '命令被拒绝', undefined, {
          event_type: 'tool_error',
          tool_name: 'exec',
          risk_level: 'high',
        }),
      ],
    )

    expect(next).toHaveLength(2)
    expect(next[0].content).toBe('[QQ群 42] [需要确认 (ABC123)] 需要确认高风险动作')
    expect(next[1].content).toBe('[QQ群 42] [工具失败] 命令被拒绝')
  })

  it('formats structured stage action events as readable summaries', () => {
    const next = appendXiaomiaoBridgeEvents(
      [],
      [
        bridgeEvent(11, 'qq-group', 'assistant', JSON.stringify({
          service: 'stage',
          action: 'background',
          payload: { id: 'builtin:cozy-tea-corner' },
        }), undefined, {
          event_type: 'stage_action',
          result_summary: 'background',
        }),
        bridgeEvent(12, 'qq-group', 'assistant', JSON.stringify({
          service: 'stage',
          action: 'emotion',
          payload: { name: 'happy', intensity: 1 },
        }), undefined, {
          event_type: 'stage_action',
          result_summary: 'stage:emotion',
        }),
      ],
    )

    expect(next).toHaveLength(2)
    expect(next[0].content).toBe('[QQ群 42] [舞台动作:background] 目标：builtin:cozy-tea-corner')
    expect(next[1].content).toBe('[QQ群 42] [舞台动作:emotion] 表情：happy')
  })

  it('syncs bridge events through the shared polling helper', async () => {
    let messages: ChatHistoryItem[] = []
    const onEvents = vi.fn()
    const requestEvents = vi.fn(async () => ({
      lastId: 14,
      events: [
        bridgeEvent(13, 'qq-private', 'user', '同步问题'),
        bridgeEvent(14, 'qq-private', 'assistant', '同步回答'),
      ],
    }))
    const sync = createXiaomiaoBridgeEventSync({
      getMessages: () => messages,
      setMessages: next => messages = next,
      requestEvents,
      onEvents,
    })

    await sync.poll()

    expect(requestEvents).toHaveBeenCalledWith({ after: 0 })
    expect(sync.getCursor()).toBe(14)
    expect(messages).toHaveLength(2)
    expect(messages[0].content).toBe('[QQ私聊 42] 同步问题')
    expect(messages[1].content).toBe('[QQ私聊 42] 同步回答')
    expect(onEvents).toHaveBeenCalledWith(expect.arrayContaining([
      expect.objectContaining({ id: 13 }),
      expect.objectContaining({ id: 14 }),
    ]))
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

    expect(calls[0]).toBe('http://127.0.0.1:8900/v1/xiaomiao/config')
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

function bridgeEvent(
  id: number,
  source: string,
  role: 'user' | 'assistant',
  content: string,
  clientMessageId?: string,
  metadata: Record<string, string> = {},
) {
  const event = {
    id,
    source,
    channel: source,
    chat_id: '42',
    user_id: 42,
    role,
    content,
    timestamp: 1780399500 + id,
    ...(clientMessageId ? { client_message_id: clientMessageId } : {}),
    ...metadata,
  }
  return {
    ...event,
    schema_version: 1,
    conversation_id: `${event.channel}:${event.chat_id}`,
    message_id: clientMessageId
      ? `client:${clientMessageId}:${event.role}`
      : `bridge:${event.id}`,
  }
}

function jsonResponse(payload: unknown) {
  return {
    ok: true,
    status: 200,
    json: async () => payload,
  } as Response
}
