import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { createMinecraftContext } from '../chat/context-providers/minecraft'
import { useMinecraftStore } from './gaming-minecraft'

const channel = vi.hoisted(() => {
  const listeners = new Map<string, (event: any) => void>()

  return {
    listeners,
    onContextUpdate: vi.fn((callback: (event: any) => void) => {
      listeners.set('context:update', callback)
      return vi.fn()
    }),
    onEvent: vi.fn((type: string, callback: (event: any) => void) => {
      listeners.set(type, callback)
      return vi.fn()
    }),
  }
})

vi.mock('../mods/api/channel-server', () => ({
  useModsServerChannelStore: () => channel,
}))

describe('minecraft game companion state', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    channel.listeners.clear()
    channel.onContextUpdate.mockClear()
    channel.onEvent.mockClear()
  })

  afterEach(() => {
    useMinecraftStore().dispose()
  })

  it('tracks service health and runtime context from minecraft-bot events', () => {
    const store = useMinecraftStore()
    store.initialize()

    channel.listeners.get('registry:modules:health:healthy')?.({
      data: { name: 'minecraft-bot' },
    })
    channel.listeners.get('context:update')?.({
      metadata: { source: { plugin: { id: 'minecraft-bot' } } },
      data: { lane: 'minecraft:runtime', text: 'Following the player at x=12 z=-4' },
    })

    expect(store.serviceConnected).toBe(true)
    expect(store.configured).toBe(true)
    expect(store.latestRuntimeContextText).toBe('Following the player at x=12 z=-4')
    expect(store.trafficEntries).toHaveLength(1)
    expect(store.trafficEntries[0]?.source).toBe('minecraft-bot')
  })

  it('ignores unrelated services and minecraft status-only context', () => {
    const store = useMinecraftStore()
    store.initialize()

    channel.listeners.get('context:update')?.({
      metadata: { source: { plugin: { id: 'other-service' } } },
      data: { lane: 'minecraft:runtime', text: 'unrelated' },
    })
    channel.listeners.get('context:update')?.({
      metadata: { source: { plugin: { id: 'minecraft-bot' } } },
      data: { lane: 'minecraft:status', text: 'heartbeat' },
    })

    expect(store.latestRuntimeContextText).toBe('')
    expect(store.trafficEntries).toHaveLength(0)
  })

  it('projects the observed game state into the next agent turn context', () => {
    const store = useMinecraftStore()
    store.initialize()

    channel.listeners.get('registry:modules:health:healthy')?.({
      data: { identity: { plugin: { id: 'minecraft-bot' } } },
    })
    channel.listeners.get('context:update')?.({
      metadata: { source: { id: 'minecraft-bot' } },
      data: { lane: 'minecraft:runtime', text: 'Player asked me to collect oak logs' },
    })

    const context = createMinecraftContext()

    expect(context?.contextId).toBe('system:minecraft-integration')
    expect(context?.metadata?.source.plugin?.id).toBe('minecraft-bot')
    expect(context?.text).toContain('currently online')
    expect(context?.text).toContain('Player asked me to collect oak logs')
  })
})
