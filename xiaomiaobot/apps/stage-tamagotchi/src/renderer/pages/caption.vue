<script setup lang="ts">
import { defineInvoke } from '@moeru/eventa'
import { useElectronEventaContext, useElectronMouseAroundWindowBorder, useElectronMouseInWindow } from '@proj-airi/electron-vueuse'
import { refDebounced, useBroadcastChannel } from '@vueuse/core'
import { computed, onMounted, ref, watch } from 'vue'

import { syncCaptionAttachedState } from './caption-follow-state'
import { CAPTION_DETACHED_DRAG_HANDLE_CLASSES, resolveCaptionOverlayOpacityClass } from './caption-presentation'
import { captionGetIsFollowingWindow, captionIsFollowingWindowChanged } from '../../shared/eventa'

const attached = ref(false)
const speakerText = ref('')
const assistantText = ref('')
const { isOutside: isOutsideWindow } = useElectronMouseInWindow()
const isOutsideWindowFor250Ms = refDebounced(isOutsideWindow, 250)
const shouldFadeOnCursorWithin = computed(() => !isOutsideWindowFor250Ms.value)
const overlayOpacityClass = computed(() => resolveCaptionOverlayOpacityClass({
  attached: attached.value,
  shouldFadeOnCursorWithin: shouldFadeOnCursorWithin.value,
}))
const { isNearAnyBorder: isAroundWindowBorder } = useElectronMouseAroundWindowBorder({ threshold: 30 })
const isAroundWindowBorderFor250Ms = refDebounced(isAroundWindowBorder, 250)

// Broadcast channel for captions
type CaptionChannelEvent
  = | { type: 'caption-speaker', text: string }
    | { type: 'caption-assistant', text: string }
const { data } = useBroadcastChannel<CaptionChannelEvent, CaptionChannelEvent>({ name: 'airi-caption-overlay' })

const context = useElectronEventaContext()
const getAttached = defineInvoke(context.value, captionGetIsFollowingWindow)

onMounted(async () => {
  try {
    context.value.on(captionIsFollowingWindowChanged, (event) => {
      attached.value = Boolean(event?.body)
    })
  }
  catch {}

  try {
    await syncCaptionAttachedState({
      getAttached,
      onResolved: (isAttached) => {
        attached.value = isAttached
      },
    })
  }
  catch {}

  try {
    // Update texts from broadcast channel
    watch(data, (event) => {
      if (!event)
        return
      if (event.type === 'caption-speaker') {
        speakerText.value = event.text
      }
      else if (event.type === 'caption-assistant') {
        assistantText.value = event.text
      }
    }, { immediate: true })
  }
  catch {}
})
</script>

<template>
  <div class="pointer-events-none relative h-full w-full flex items-end justify-center">
    <div
      :class="[
        overlayOpacityClass,
        'pointer-events-auto relative select-none rounded-xl px-3 py-2',
        'transition-opacity duration-250 ease-in-out',
      ]"
    >
      <div
        v-show="!attached"
        :class="CAPTION_DETACHED_DRAG_HANDLE_CLASSES"
        title="Drag to move"
      >
        <div class="h-[4px] w-16 rounded-full bg-[rgba(255,255,255,0.85)]" />
      </div>

      <div class="max-w-[80vw] flex flex-col gap-1">
        <div
          v-if="speakerText"
          class="rounded-md px-2 py-1 text-[1.1rem] text-neutral-50 font-medium text-shadow-lg text-shadow-color-neutral-900/60"
        >
          {{ speakerText }}
        </div>
        <div
          v-if="assistantText"
          class="rounded-md px-2 py-1 text-[1.35rem] text-primary-50 font-semibold text-stroke-4 text-stroke-primary-300/50 text-shadow-lg text-shadow-color-primary-700/50"
          :style="{ paintOrder: 'stroke fill' }"
        >
          {{ assistantText }}
        </div>
      </div>
    </div>

    <Transition
      enter-active-class="transition-opacity duration-250 ease-in-out"
      enter-from-class="opacity-50"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-250 ease-in-out"
      leave-from-class="opacity-100"
      leave-to-class="opacity-50"
    >
      <div v-if="isAroundWindowBorderFor250Ms" class="pointer-events-none absolute left-0 top-0 z-999 h-full w-full">
        <div
          :class="[
            'b-primary/50',
            'h-full w-full animate-flash animate-duration-3s animate-count-infinite b-4 rounded-2xl',
          ]"
        />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
</style>

<route lang="yaml">
meta:
  layout: stage
</route>
