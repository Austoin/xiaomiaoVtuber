import type { ContextMessage } from '../../types/chat'

import { ContextUpdateStrategy } from '@proj-airi/server-sdk'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import { useChatContextStore } from './context-store'

function createContext(contextId: string, pluginId: string): ContextMessage {
  return {
    id: `${contextId}-message`,
    contextId,
    strategy: ContextUpdateStrategy.ReplaceSelf,
    text: `${contextId} text`,
    createdAt: Date.now(),
    metadata: {
      source: {
        id: `${pluginId}-instance`,
        kind: 'plugin',
        plugin: { id: pluginId },
      },
    },
  }
}

describe('chat context store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('removes only active entries matching a context id', () => {
    const store = useChatContextStore()
    store.ingestContextMessage(createContext('system:minecraft-integration', 'minecraft-bot'))
    store.ingestContextMessage(createContext('system:weather', 'weather-service'))

    expect(store.removeContextsByContextId('system:minecraft-integration')).toBe(1)
    expect(store.getContextsSnapshot()).toEqual({
      'weather-service:weather-service-instance': [
        expect.objectContaining({ contextId: 'system:weather' }),
      ],
    })
  })

  it('preserves active context identity when no entry matches', () => {
    const store = useChatContextStore()
    store.ingestContextMessage(createContext('system:weather', 'weather-service'))
    const activeContexts = store.activeContexts

    expect(store.removeContextsByContextId('system:minecraft-integration')).toBe(0)
    expect(store.activeContexts).toBe(activeContexts)
  })
})
