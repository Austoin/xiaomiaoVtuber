import { useLocalStorage } from '@vueuse/core'
import { defineStore } from 'pinia'

export const useControlsIslandStore = defineStore('controls-island', () => {
  // Persist fade-on-hover preference per user
  const fadeOnHoverEnabled = useLocalStorage<boolean>('controls-island/fade-on-hover-enabled', false)
  const dontShowItAgainNoticeFadeOnHover = useLocalStorage<boolean>('preferences/dont-show-it-again/notice/fade-on-hover', false)

  // NOTICE:
  // The stage main window becomes fully click-through when this persisted flag remains true,
  // which makes the controls island appear to disappear after restart even though the UI still exists.
  // Root cause: `index.vue` derives both opacity and `setIgnoreMouseEvents(true)` from this value.
  // Source/context: `src/renderer/pages/index.vue:124` and `src/renderer/pages/index.vue:211`.
  // Removal condition: only remove this normalization after the fade-on-hover UX no longer hides
  // critical controls or after the feature gains a safe recovery path on startup.
  fadeOnHoverEnabled.value = false

  function enableFadeOnHover() {
    fadeOnHoverEnabled.value = true
  }

  function disableFadeOnHover() {
    fadeOnHoverEnabled.value = false
  }

  return {
    fadeOnHoverEnabled,
    dontShowItAgainNoticeFadeOnHover,
    enableFadeOnHover,
    disableFadeOnHover,
  }
})
