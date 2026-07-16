import type { ChatHistoryItem } from '@proj-airi/stage-ui/types/chat'

import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { requestXiaomiaoBridgeReply } from '@proj-airi/stage-layouts/xiaomiao-bridge'
import { describe, expect, it, vi } from 'vitest'

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

describe('xiaomiaoAgent client', () => {
  it('sends chat directly to the unified xiaomiaoAgent session', async () => {
    const fetcher = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => ({
        choices: [{ message: { content: 'agent reply' } }],
      }),
    })) as unknown as typeof globalThis.fetch

    const reply = await requestXiaomiaoBridgeReply({
      text: 'hello',
      clientMessageId: 'client-1',
      fetcher,
    })

    expect(reply).toBe('agent reply')
    const [url, init] = vi.mocked(fetcher).mock.calls[0]
    expect(url).toBe('http://127.0.0.1:8900/v1/chat/completions')
    expect(JSON.parse(String(init?.body))).toEqual({
      session_id: 'xiaomiao-unified',
      channel: 'web',
      chat_id: 'stage-client',
      user_id: 'stage-client',
      client_message_id: 'client-1',
      messages: [{ role: 'user', content: 'hello' }],
    })
  })

  it('keeps shared chat components free of local agent execution', () => {
    const componentRoot = resolve(
      import.meta.dirname,
      '../../../../../packages/stage-layouts/src/components',
    )
    const sources = [
      readFileSync(resolve(componentRoot, 'Widgets/ChatArea.vue'), 'utf8'),
      readFileSync(resolve(componentRoot, 'Layouts/MobileInteractiveArea.vue'), 'utf8'),
    ]

    for (const source of sources) {
      expect(source).not.toContain('isStageWeb')
      expect(source).not.toContain('chatOrchestrator.ingest')
      expect(source).not.toContain('await ingest(')
      expect(source).toContain('appendXiaomiaoBridgeReply')
    }
  })

  it('keeps Pocket voice chat on the unified agent client', () => {
    const source = readFileSync(
      resolve(import.meta.dirname, '../../../../stage-pocket/src/pages/index.vue'),
      'utf8',
    )

    expect(source).not.toContain('getProviderInstance')
    expect(source).not.toContain('chatStore.ingest')
    expect(source).toContain('appendXiaomiaoBridgeReply')
    expect(source).toContain('appendXiaomiaoBridgeError')
  })

  it('does not fall back from chat sync to a local provider', () => {
    const source = readFileSync(
      resolve(import.meta.dirname, '../stores/chat-sync.ts'),
      'utf8',
    )

    expect(source).not.toContain('tryIngestViaXiaomiaoBridge')
    expect(source).not.toContain('getProviderInstance')
    expect(source).not.toContain('chatOrchestrator.ingest')
    expect(source).toContain('appendXiaomiaoBridgeReply')
  })

  it('routes the shared chat orchestrator through xiaomiaoAgent', () => {
    const source = readFileSync(
      resolve(import.meta.dirname, '../../../../../packages/stage-ui/src/stores/chat.ts'),
      'utf8',
    )

    expect(source).not.toContain('llmStore.stream')
    expect(source).not.toContain('from \'./llm\'')
    expect(source).toContain('requestXiaomiaoAgentReply')
  })

  it('does not gate context input on a frontend provider', () => {
    const source = readFileSync(
      resolve(import.meta.dirname, '../../../../../packages/stage-ui/src/stores/mods/api/context-bridge.ts'),
      'utf8',
    )

    expect(source).not.toContain('getProviderInstance')
    expect(source).not.toContain('activeProvider')
    expect(source).toContain('chatOrchestrator.ingest')
  })

  it('keeps performance playground chat on xiaomiaoAgent', () => {
    const sources = [
      resolve(import.meta.dirname, '../../../../stage-web/src/pages/devtools/performance-playground.vue'),
      resolve(import.meta.dirname, '../../../../stage-pocket/src/pages/devtools/performance-playground.vue'),
    ].map(path => readFileSync(path, 'utf8'))

    for (const source of sources) {
      expect(source).not.toContain('activeChatProvider')
      expect(source).not.toContain('chatProvider: provider')
      expect(source).toContain('chatOrchestrator.ingest(content, {})')
    }
  })

  it('routes vision inference through xiaomiaoAgent', () => {
    const source = readFileSync(
      resolve(import.meta.dirname, '../../../../../packages/stage-ui/src/composables/vision/use-vision-inference.ts'),
      'utf8',
    )

    expect(source).not.toContain('getProviderInstance')
    expect(source).not.toContain('useLLM')
    expect(source).toContain('requestXiaomiaoAgentReply')
  })

  it('routes autonomous artistry analysis through xiaomiaoAgent', () => {
    const source = readFileSync(
      resolve(import.meta.dirname, '../../../../../packages/stage-ui/src/stores/modules/artistry-autonomous.ts'),
      'utf8',
    )

    expect(source).not.toContain('generateText')
    expect(source).not.toContain('useProvidersStore')
    expect(source).toContain('requestXiaomiaoAgentReply')
  })

  it('routes character spark notifications through xiaomiaoAgent', () => {
    const source = readFileSync(
      resolve(import.meta.dirname, '../../../../../packages/stage-ui/src/stores/character/orchestrator/store.ts'),
      'utf8',
    )

    expect(source).not.toContain('useLLM')
    expect(source).not.toContain('useProvidersStore')
    expect(source).not.toContain('setupAgentSparkNotifyHandler')
    expect(source).toContain('requestXiaomiaoAgentReply')
  })

  it('keeps markdown stress requests on xiaomiaoAgent', () => {
    const source = readFileSync(
      resolve(import.meta.dirname, '../../../../../packages/stage-ui/src/stores/markdown-stress.ts'),
      'utf8',
    )

    expect(source).not.toContain('useLLM')
    expect(source).not.toContain('getProviderInstance')
    expect(source).not.toContain('ChatProvider')
    expect(source).toContain('chatStore.ingest(message.text, {})')
  })
})
