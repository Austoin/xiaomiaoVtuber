export interface XiaomiaoBridgeState {
  replyText: string
  timestamp: number
  userId: number
}

/**
 * Decides whether a freshly fetched XiaoMiao reply should replace the overlay text.
 *
 * Use when:
 * - polling the local bridge from a renderer
 * - duplicate bridge payloads should not trigger visible re-renders
 *
 * Expects:
 * - timestamps come from the XiaoMiao state endpoint
 * - text values are already normalized for display
 *
 * Returns:
 * - `true` when the next payload is newer or text content changed
 * - `false` when the payload is a duplicate of the current visible state
 */
export function shouldAdoptXiaomiaoBridgeState(
  currentTimestamp: number,
  nextTimestamp: number,
  currentText: string,
  nextText: string,
): boolean {
  return nextTimestamp > currentTimestamp || nextText !== currentText
}

interface RawXiaomiaoBridgeState {
  reply_text?: string
  timestamp?: number
  user_id?: number
}

/**
 * Reads the latest XiaoMiao bridge reply for a single bound user.
 *
 * Use when:
 * - the desktop stage needs a visible reaction to QQ-side replies
 * - a renderer wants the latest bridge state without importing bot internals
 *
 * Expects:
 * - `fetcher` behaves like `window.fetch`
 * - `userId` is the bound XiaoMiao / QQ user identifier
 *
 * Returns:
 * - a normalized reply payload when the bridge responds with visible text
 * - `null` when the bridge is unavailable or has no displayable reply
 */
export async function readXiaomiaoBridgeState(
  fetcher: (input: string) => Promise<{ ok: boolean, json: () => Promise<RawXiaomiaoBridgeState> }>,
  userId: number,
): Promise<XiaomiaoBridgeState | null> {
  const response = await fetcher(`http://127.0.0.1:5519/v1/xiaomiao/state?user_id=${userId}`)
  if (!response.ok) {
    return null
  }

  const payload = await response.json()
  const replyText = payload.reply_text?.trim()
  if (!replyText) {
    return null
  }

  return {
    replyText,
    timestamp: payload.timestamp ?? 0,
    userId: payload.user_id ?? userId,
  }
}
