import type { ChatHistoryItem } from '@proj-airi/stage-ui/types/chat'

import { describe, expect, it } from 'vitest'

import { appendBridgeAssistantReply } from './xiaomiao-bridge-chat'

/**
 * @example
 * describe('appendBridgeAssistantReply', () => {
 *   it('appends a fresh assistant reply from the QQ bridge', () => {})
 * })
 */
describe('appendBridgeAssistantReply', () => {
  /**
   * @example
   * it('appends a fresh assistant reply from the QQ bridge', () => {
   *   // current session ends with a user message
   *   // bridge emits a new assistant reply
   *   // helper appends one assistant history entry
   * })
   */
  it('appends a fresh assistant reply from the QQ bridge', () => {
    const messages: ChatHistoryItem[] = [
      { role: 'user', content: 'hello', createdAt: 1, id: 'user-1' },
    ]

    const nextMessages = appendBridgeAssistantReply(messages, 'bridge reply', 2)

    expect(nextMessages).toHaveLength(2)
    expect(nextMessages[1]).toEqual(expect.objectContaining({
      role: 'assistant',
      content: 'bridge reply',
      createdAt: 2,
    }))
  })

  /**
   * @example
   * it('skips duplicate assistant replies that already exist at the tail', () => {
   *   // current session already ends with the same assistant reply
   *   // bridge polling sees the same payload again
   *   // helper keeps the history unchanged
   * })
   */
  it('skips duplicate assistant replies that already exist at the tail', () => {
    const messages: ChatHistoryItem[] = [
      { role: 'user', content: 'hello', createdAt: 1, id: 'user-1' },
      { role: 'assistant', content: 'bridge reply', slices: [], tool_results: [], createdAt: 2, id: 'assistant-1' },
    ]

    const nextMessages = appendBridgeAssistantReply(messages, 'bridge reply', 3)

    expect(nextMessages).toEqual(messages)
  })
})
