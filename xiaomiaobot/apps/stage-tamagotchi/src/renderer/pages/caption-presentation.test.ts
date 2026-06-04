import { describe, expect, it } from 'vitest'

import { CAPTION_DETACHED_DRAG_HANDLE_CLASSES, resolveCaptionOverlayOpacityClass } from './caption-presentation'

/**
 * Caption overlay presentation rules for detached/following states.
 */
describe('caption presentation', () => {
  /**
   * @example
   * expect(resolveCaptionOverlayOpacityClass({ attached: false, shouldFadeOnCursorWithin: true })).toBe('op-100')
   */
  it('keeps detached caption visible while repositioning', () => {
    expect(resolveCaptionOverlayOpacityClass({ attached: false, shouldFadeOnCursorWithin: true })).toBe('op-100')
    expect(resolveCaptionOverlayOpacityClass({ attached: false, shouldFadeOnCursorWithin: false })).toBe('op-100')
  })

  /**
   * @example
   * expect(resolveCaptionOverlayOpacityClass({ attached: true, shouldFadeOnCursorWithin: true })).toBe('op-0')
   */
  it('preserves fade-on-hover only while attached', () => {
    expect(resolveCaptionOverlayOpacityClass({ attached: true, shouldFadeOnCursorWithin: true })).toBe('op-0')
    expect(resolveCaptionOverlayOpacityClass({ attached: true, shouldFadeOnCursorWithin: false })).toBe('op-100')
  })

  /**
   * @example
   * expect(CAPTION_DETACHED_DRAG_HANDLE_CLASSES).toContain('w-[160px]')
   */
  it('uses an expanded drag handle for detached mode', () => {
    expect(CAPTION_DETACHED_DRAG_HANDLE_CLASSES).toContain('w-[160px]')
    expect(CAPTION_DETACHED_DRAG_HANDLE_CLASSES).toContain('h-[24px]')
  })
})
