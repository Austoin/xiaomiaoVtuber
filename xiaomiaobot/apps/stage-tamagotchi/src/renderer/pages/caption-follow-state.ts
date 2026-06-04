export interface SyncCaptionAttachedStateOptions {
  /** Reads the latest follow-window state from the Electron main process. */
  getAttached: () => Promise<boolean>
  /** Applies the resolved attached state to the Vue side. */
  onResolved: (attached: boolean) => void
  /** Max retry attempts before giving up. @default 4 */
  maxAttempts?: number
  /** Delay in milliseconds between retries. @default 80 */
  retryDelayMs?: number
}

function wait(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Synchronizes the caption follow-window state from the Electron main process.
 *
 * Use when:
 * - the caption renderer boots before the main-process invoke handler is ready
 * - the window must recover from a missed `captionIsFollowingWindowChanged` event
 *
 * Expects:
 * - `getAttached` throws while the invoke channel is still booting
 * - `onResolved` can safely update local renderer state each time a value resolves
 *
 * Returns:
 * - resolves after the first successful attached-state fetch
 * - silently stops after the retry budget is exhausted
 */
export async function syncCaptionAttachedState(options: SyncCaptionAttachedStateOptions): Promise<void> {
  const maxAttempts = options.maxAttempts ?? 4
  const retryDelayMs = options.retryDelayMs ?? 80

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      options.onResolved(Boolean(await options.getAttached()))
      return
    }
    catch {
      if (attempt === maxAttempts) {
        return
      }

      await wait(retryDelayMs)
    }
  }
}
