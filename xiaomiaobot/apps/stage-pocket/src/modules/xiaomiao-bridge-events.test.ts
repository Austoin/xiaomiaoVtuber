import type { ChatHistoryItem } from '@proj-airi/stage-ui/types/chat'
import type { XiaomiaoBridgeEvent } from '@proj-airi/stage-layouts/xiaomiao-bridge'

import { describe, expect, it, vi } from 'vitest'

import { createStagePocketBridgeEventSync } from './xiaomiao-bridge-events'

describe('createStagePocketBridgeEventSync', () => {
  it('polls bridge events and appends them to pocket chat history', async () => {
    let messages: ChatHistoryItem[] = []
    const requestEvents = vi.fn(async () => ({
      lastId: 2,
      events: [
        bridgeEvent(1, 'qq-group', 'user', '群里问'),
        bridgeEvent(2, 'qq-group', 'assistant', '群里答', undefined, {
          event_type: 'tool_finish',
          tool_name: 'xiaomiaobot_status',
        }),
      ],
    }))
    const sync = createStagePocketBridgeEventSync({
      getMessages: () => messages,
      setMessages: next => messages = next,
      requestEvents,
    })

    await sync.poll()

    expect(requestEvents).toHaveBeenCalledWith({ after: 0 })
    expect(sync.getCursor()).toBe(2)
    expect(messages).toHaveLength(2)
    expect(messages[0].content).toBe('[QQ群 42] 群里问')
    expect(messages[1].content).toBe('[QQ群 42] [工具完成:xiaomiaobot_status] 群里答')
  })

  it('skips duplicate bridge events through stable message ids', async () => {
    let messages: ChatHistoryItem[] = []
    const event = bridgeEvent(3, 'qq-private', 'assistant', '同一条')
    const requestEvents = vi.fn(async () => ({
      lastId: 3,
      events: [event],
    }))
    const sync = createStagePocketBridgeEventSync({
      getMessages: () => messages,
      setMessages: next => messages = next,
      requestEvents,
    })

    await sync.poll()
    await sync.poll()

    expect(messages).toHaveLength(1)
    expect(messages[0].id).toBe('xiaomiao-event-3')
    expect(requestEvents).toHaveBeenLastCalledWith({ after: 3 })
  })

  it('logs polling failures without mutating chat history', async () => {
    const messages: ChatHistoryItem[] = []
    const logger = { error: vi.fn() }
    const sync = createStagePocketBridgeEventSync({
      getMessages: () => messages,
      setMessages: vi.fn(),
      requestEvents: vi.fn(async () => {
        throw new Error('bridge offline')
      }),
      logger,
    })

    await sync.poll()

    expect(messages).toEqual([])
    expect(logger.error).toHaveBeenCalledWith(
      'Failed to sync XiaoMiao bridge events in stage-pocket:',
      expect.any(Error),
    )
  })

  it('starts and stops polling with one interval', () => {
    let scheduled: (() => void) | undefined
    const clearIntervalFn = vi.fn()
    const setIntervalFn = vi.fn((callback: () => void) => {
      scheduled = callback
      return 7 as unknown as ReturnType<typeof setInterval>
    })
    const requestEvents = vi.fn(async () => ({
      lastId: 0,
      events: [],
    }))
    const sync = createStagePocketBridgeEventSync({
      getMessages: () => [],
      setMessages: vi.fn(),
      requestEvents,
      setIntervalFn: setIntervalFn as unknown as typeof setInterval,
      clearIntervalFn: clearIntervalFn as unknown as typeof clearInterval,
      pollIntervalMs: 10,
    })

    sync.start()
    sync.start()
    scheduled?.()
    sync.stop()
    sync.stop()

    expect(sync.isRunning()).toBe(false)
    expect(setIntervalFn).toHaveBeenCalledTimes(1)
    expect(setIntervalFn).toHaveBeenCalledWith(expect.any(Function), 10)
    expect(clearIntervalFn).toHaveBeenCalledTimes(1)
    expect(requestEvents).toHaveBeenCalled()
  })
})

function bridgeEvent(
  id: number,
  source: string,
  role: 'user' | 'assistant',
  content: string,
  clientMessageId?: string,
  metadata: Partial<XiaomiaoBridgeEvent> = {},
): XiaomiaoBridgeEvent {
  return {
    id,
    schema_version: 1,
    conversation_id: `${source}:42`,
    message_id: clientMessageId ? `client:${clientMessageId}:${role}` : `bridge:${id}`,
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
}
