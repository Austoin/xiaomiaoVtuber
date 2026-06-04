import { ref } from 'vue'

import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const storageState = new Map<string, ReturnType<typeof ref<boolean>>>()

vi.mock('@vueuse/core', () => ({
  useLocalStorage: vi.fn((key: string, defaultValue: boolean) => {
    if (!storageState.has(key)) {
      storageState.set(key, ref(defaultValue))
    }

    return storageState.get(key)!
  }),
}))

/**
 * @example
 * describe('useControlsIslandStore', () => {
 *   it('resets persisted fade-on-hover so the main controls stay visible', () => {})
 * })
 */
describe('useControlsIslandStore', async () => {
  const { useControlsIslandStore } = await import('./controls-island')

  beforeEach(() => {
    storageState.clear()
    setActivePinia(createPinia())
  })

  /**
   * @example
   * it('resets persisted fade-on-hover so the main controls stay visible', () => {
   *   // a previous session persisted fade-on-hover = true
   *   // current startup should normalize it back to false
   *   // so the stage controls remain visible after restart
   * })
   */
  it('resets persisted fade-on-hover so the main controls stay visible', () => {
    storageState.set('controls-island/fade-on-hover-enabled', ref(true))

    const store = useControlsIslandStore()

    expect(store.fadeOnHoverEnabled).toBe(false)
  })
})
