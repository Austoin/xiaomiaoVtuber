export interface CaptionOverlayOpacityParams {
  /** Whether the caption window is currently attached/following the main window. */
  attached: boolean
  /** Whether the cursor is currently inside the caption window fade trigger area. */
  shouldFadeOnCursorWithin: boolean
}

/**
 * Resolves the caption overlay opacity class.
 *
 * Use when:
 * - rendering the detached caption overlay window
 * - deciding whether the overlay should fade while attached to the main stage
 *
 * Expects:
 * - `attached` reflects the latest follow-window state from the main process
 * - `shouldFadeOnCursorWithin` comes from the current pointer/fade heuristic
 *
 * Returns:
 * - `op-0` only for attached overlays that intentionally fade under the cursor
 * - `op-100` for every detached/repositionable state
 */
export function resolveCaptionOverlayOpacityClass(params: CaptionOverlayOpacityParams): 'op-0' | 'op-100' {
  if (!params.attached) {
    return 'op-100'
  }

  return params.shouldFadeOnCursorWithin ? 'op-0' : 'op-100'
}

/**
 * Detached caption drag handle classes.
 *
 * Before:
 * - `h-[14px] w-[36px]`
 *
 * After:
 * - `h-[24px] w-[160px]`
 */
export const CAPTION_DETACHED_DRAG_HANDLE_CLASSES = [
  '[-webkit-app-region:drag]',
  'absolute',
  'left-1/2',
  'h-[24px]',
  'w-[160px]',
  'border',
  'border-[rgba(125,125,125,0.35)]',
  'rounded-[12px]',
  'bg-[rgba(125,125,125,0.32)]',
  'backdrop-blur-[6px]',
  '-top-3',
  '-translate-x-1/2',
  'flex',
  'items-center',
  'justify-center',
].join(' ')
