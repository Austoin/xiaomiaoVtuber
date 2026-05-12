import { afterEach, describe, expect, it, vi } from 'vitest'

import { syncCaptionAttachedState } from './caption-follow-state'

/**
 * Caption attached-state recovery for late main-process event registration.
 */
describe('caption follow state sync', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  /**
   * @example
   * await syncCaptionAttachedState({ getAttached, onResolved: value => resolved = value })
   */
  it('retries the follow-state invoke until the main process becomes ready', async () => {
    vi.useFakeTimers()

    let attempts = 0
    let resolved: boolean | undefined

    const pending = syncCaptionAttachedState({
      getAttached: async () => {
        attempts += 1
        if (attempts < 3) {
          throw new Error('invoke not ready')
        }

        return false
      },
      onResolved: (value) => {
        resolved = value
      },
    })

    await vi.runAllTimersAsync()
    await pending

    expect(attempts).toBe(3)
    expect(resolved).toBe(false)
  })
})
