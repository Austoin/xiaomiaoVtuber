import type { WebSocketEventOf } from '@proj-airi/server-sdk'

import { createTestingPinia } from '@pinia/testing'
import { tool } from '@xsai/tool'
import { setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { sparkNotifyCommandSchema, useCharacterOrchestratorStore } from '.'
import { useCharacterStore } from '..'
import { useAiriCardStore } from '../../modules'

const requestXiaomiaoAgentReply = vi.hoisted(() => vi.fn())

vi.mock('../../../libs/xiaomiao-agent', () => ({ requestXiaomiaoAgentReply }))
vi.mock('vue-i18n', () => ({
  createI18n: () => ({ global: { locale: { value: 'en' }, t: (key: string) => key } }),
  useI18n: () => ({ t: (key: string) => key }),
}))

function notifyEvent(): WebSocketEventOf<'spark:notify'> {
  return {
    type: 'spark:notify',
    source: 'minecraft',
    data: {
      id: 'notify-1',
      eventId: 'event-1',
      kind: 'alarm',
      urgency: 'immediate',
      headline: 'Hit by zombie',
      destinations: ['character'],
    },
  }
}

describe('sparkNotifyCommandSchema', () => {
  it('emits a strict root object schema', async () => {
    const sparkTool = await tool({
      name: 'builtIn_sparkCommand',
      description: 'test',
      parameters: sparkNotifyCommandSchema,
      execute: async () => undefined,
    })

    expect(sparkTool.function.parameters).toEqual(expect.objectContaining({
      type: 'object',
      additionalProperties: false,
    }))
  })
})

describe('character orchestrator', () => {
  beforeEach(() => {
    setActivePinia(createTestingPinia({ createSpy: vi.fn, stubActions: false }))
    requestXiaomiaoAgentReply.mockReset()
    requestXiaomiaoAgentReply.mockResolvedValue('Ahhh, got hit by zombie!')
    // @ts-expect-error testing a computed character prompt
    useAiriCardStore().systemPrompt = 'You are Xiaomiao.'
  })

  it('routes immediate notifications through xiaomiaoAgent', async () => {
    const characterStore = useCharacterStore()
    characterStore.onSparkNotifyReactionStreamEvent = vi.fn()
    characterStore.onSparkNotifyReactionStreamEnd = vi.fn()
    const store = useCharacterOrchestratorStore()

    const result = await store.handleSparkNotify(notifyEvent())

    expect(result).toEqual({ commands: [] })
    expect(requestXiaomiaoAgentReply).toHaveBeenCalledWith(expect.objectContaining({
      clientMessageId: 'stage-spark-notify-1',
      text: expect.stringContaining('Hit by zombie'),
    }))
    expect(characterStore.onSparkNotifyReactionStreamEvent).toHaveBeenCalledWith(
      'notify-1',
      'Ahhh, got hit by zombie!',
    )
    expect(characterStore.onSparkNotifyReactionStreamEnd).toHaveBeenCalledWith(
      'notify-1',
      'Ahhh, got hit by zombie!',
    )
  })

  it('includes runtime message overrides in the Agent request', async () => {
    const store = useCharacterOrchestratorStore()

    await store.handleSparkNotify(notifyEvent(), {
      forceTextResponse: true,
      messageOverride: {
        appendSystemInstructions: ['Plugin-specific hint'],
        appendUserSections: ['Rendered board snapshot'],
      },
    })

    const request = requestXiaomiaoAgentReply.mock.calls[0][0]
    expect(request.text).toContain('Plugin-specific hint')
    expect(request.text).toContain('Rendered board snapshot')
  })

  it('exposes Agent failures and ends the reaction', async () => {
    const characterStore = useCharacterStore()
    characterStore.onSparkNotifyReactionStreamEnd = vi.fn()
    requestXiaomiaoAgentReply.mockRejectedValue(new Error('Agent unavailable'))
    const store = useCharacterOrchestratorStore()

    await expect(store.handleSparkNotify(notifyEvent())).rejects.toThrow('Agent unavailable')
    expect(characterStore.onSparkNotifyReactionStreamEnd).toHaveBeenCalledWith('notify-1', '')
  })
})
