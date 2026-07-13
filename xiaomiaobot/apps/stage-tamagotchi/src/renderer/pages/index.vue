<script setup lang="ts">
import type { ModelSettingsRuntimeSnapshot } from '@proj-airi/stage-ui/components/scenarios/settings/model-settings/runtime'
import type { ChatHistoryItem } from '@proj-airi/stage-ui/types/chat'

import type { ModelSettingsRuntimeChannelEvent } from '../../shared/model-settings-runtime'
import type { XiaomiaoStageActionRejection } from './xiaomiao-bridge-reaction'

import workletUrl from '@proj-airi/stage-ui/workers/vad/process.worklet?worker&url'

import { tryCatch } from '@moeru/std'
import { electron } from '@proj-airi/electron-eventa'
import {
  useElectronEventaInvoke,
  useElectronMouseAroundWindowBorder,
  useElectronMouseInElement,
  useElectronMouseInWindow,
  useElectronRelativeMouse,
} from '@proj-airi/electron-vueuse'
import { createXiaomiaoBridgeEventSync } from '@proj-airi/stage-layouts/xiaomiao-bridge'
import { useModelStore, useThreeSceneIsTransparentAtPoint } from '@proj-airi/stage-ui-three'
import { HoloCoupon } from '@proj-airi/stage-ui/components'
import {
  createEmptyModelSettingsRuntimeSnapshot,
  resolveComponentStateToRuntimePhase,
} from '@proj-airi/stage-ui/components/scenarios/settings/model-settings/runtime'
import { WidgetStage } from '@proj-airi/stage-ui/components/scenes'
import { useAudioRecorder } from '@proj-airi/stage-ui/composables/audio/audio-recorder'
import { useCanvasPixelIsTransparentAtPoint } from '@proj-airi/stage-ui/composables/canvas-alpha'
import { EMOTION_VALUES } from '@proj-airi/stage-ui/constants/emotions'
import { useVAD } from '@proj-airi/stage-ui/stores/ai/models/vad'
import { useBackgroundStore } from '@proj-airi/stage-ui/stores/background'
import { useCharacterStore } from '@proj-airi/stage-ui/stores/character'
import { useChatSessionStore } from '@proj-airi/stage-ui/stores/chat/session-store'
import { useDisplayModelsStore } from '@proj-airi/stage-ui/stores/display-models'
import { useLive2d } from '@proj-airi/stage-ui/stores/live2d'
import { useAiriCardStore } from '@proj-airi/stage-ui/stores/modules/airi-card'
import { useHearingSpeechInputPipeline } from '@proj-airi/stage-ui/stores/modules/hearing'
import { useSpeechStore } from '@proj-airi/stage-ui/stores/modules/speech'
import { useOnboardingStore } from '@proj-airi/stage-ui/stores/onboarding'
import { useProvidersStore } from '@proj-airi/stage-ui/stores/providers'
import { useSettings, useSettingsAudioDevice } from '@proj-airi/stage-ui/stores/settings'
import { refDebounced, useBroadcastChannel } from '@vueuse/core'
import { storeToRefs } from 'pinia'
import { computed, onMounted, onUnmounted, ref, toRef, watch } from 'vue'

import ControlsIsland from '../components/stage-islands/controls-island/index.vue'
import ResourceStatusIsland from '../components/stage-islands/resource-status-island/index.vue'
import StatusIsland from '../components/stage-islands/status-island/index.vue'

import { electronOpenOnboarding } from '../../shared/eventa'
import { modelSettingsRuntimeSnapshotChannelName } from '../../shared/model-settings-runtime'
import { useChatSyncStore } from '../stores/chat-sync'
import { useControlsIslandStore } from '../stores/controls-island'
import { useStageWindowLifecycleStore } from '../stores/stage-window-lifecycle'
import { useWindowStore } from '../stores/window'
import { shouldSampleStageTransparency } from '../utils/stage-three-transparency'
import { readXiaomiaoBridgeState } from './xiaomiao-bridge'
import {
  applyXiaomiaoBridgeReaction,
  applyXiaomiaoStageActionEvents,
  ensureBridgeSpeechReady as ensureBridgeSpeechReadyForStores,
} from './xiaomiao-bridge-reaction'

const controlsIslandRef = ref<InstanceType<typeof ControlsIsland>>()
const statusIslandRef = ref<InstanceType<typeof StatusIsland>>()
const widgetStageRef = ref<InstanceType<typeof WidgetStage>>()
const stageCanvas = toRef(() => widgetStageRef.value?.canvasElement())
const componentStateStage = ref<'pending' | 'loading' | 'mounted'>('pending')
const stageMounted = computed(() => componentStateStage.value === 'mounted')
const isLoading = computed(() => !stageMounted.value)

const isIgnoringMouseEvents = ref(false)
const shouldFadeOnCursorWithin = ref(false)

const onboardingStore = useOnboardingStore()
const chatSession = useChatSessionStore()
const characterStore = useCharacterStore()
const speechStore = useSpeechStore()
const providersStore = useProvidersStore()
const backgroundStore = useBackgroundStore()
const displayModelsStore = useDisplayModelsStore()
const airiCardStore = useAiriCardStore()
const openOnboarding = useElectronEventaInvoke(electronOpenOnboarding)

async function ensureBridgeSpeechReady() {
  const providerId = 'kokoro-local'
  const providerConfig = providersStore.getProviderConfig(providerId)
  if (!providerConfig.model) {
    providerConfig.model = 'q4f16'
  }

  await ensureBridgeSpeechReadyForStores({
    currentProvider: speechStore.activeSpeechProvider,
    currentModel: speechStore.activeSpeechModel,
    currentVoiceId: speechStore.activeSpeechVoiceId,
    providerConfigModel: String(providerConfig.model),
    loadVoices: async () => await speechStore.loadVoicesForProvider(providerId),
    applyConfig: ({ providerId, modelId, voice }) => {
      speechStore.activeSpeechProvider = providerId
      speechStore.activeSpeechModel = modelId
      speechStore.activeSpeechVoiceId = voice.id
      speechStore.activeSpeechVoice = {
        ...voice,
        name: voice.name || voice.id,
        provider: voice.provider || providerId,
        languages: (voice.languages || []).map(language => ({
          code: language.code,
          title: language.title || language.code,
        })),
      }
    },
  })
}

const { isOutside: isOutsideWindow } = useElectronMouseInWindow()
const { isOutside } = useElectronMouseInElement(controlsIslandRef)
const { isOutside: isOutsideStatusIsland } = useElectronMouseInElement(statusIslandRef)
const isOutsideFor250Ms = refDebounced(isOutside, 250)
const isOutsideStatusIslandFor250Ms = refDebounced(isOutsideStatusIsland, 250)
const { x: relativeMouseX, y: relativeMouseY } = useElectronRelativeMouse()
// NOTICE: In real-world use cases of Fade on Hover feature, the cursor may move around the edge of the
// model rapidly, causing flickering effects when checking pixel transparency strictly.
// Here we use render-target pixel sampling to keep detection aligned with the actual render output.
const isTransparentByPixels = useCanvasPixelIsTransparentAtPoint(
  stageCanvas,
  relativeMouseX,
  relativeMouseY,
  { regionRadius: 25 },
)
const isTransparentByThree = useThreeSceneIsTransparentAtPoint(
  widgetStageRef,
  relativeMouseX,
  relativeMouseY,
  { regionRadius: 25 },
)

const settingsStore = useSettings()
const { stageModelRenderer, stageModelSelectedUrl } = storeToRefs(settingsStore)
const modelStore = useModelStore()
const { sceneMutationLocked, scenePhase } = storeToRefs(modelStore)
const { stagePaused } = storeToRefs(useStageWindowLifecycleStore())
const { fadeOnHoverEnabled } = storeToRefs(useControlsIslandStore())
const modelSettingsRuntimeOwnerInstanceId = `tamagotchi-main-stage:${Math.random().toString(36).slice(2, 10)}`
const { data: modelSettingsRuntimeChannelEvent, post: postModelSettingsRuntimeChannelEvent } = useBroadcastChannel<ModelSettingsRuntimeChannelEvent, ModelSettingsRuntimeChannelEvent>({ name: modelSettingsRuntimeSnapshotChannelName })
const shouldUseThreeTransparencyHitTest = computed(() => shouldSampleStageTransparency({
  componentState: componentStateStage.value,
  fadeOnHoverEnabled: fadeOnHoverEnabled.value,
  stageModelRenderer: stageModelRenderer.value,
  stagePaused: stagePaused.value,
}))
const isTransparent = computed(() => {
  if (stagePaused.value || componentStateStage.value !== 'mounted' || !fadeOnHoverEnabled.value)
    return true

  if (stageModelRenderer.value === 'vrm')
    return shouldUseThreeTransparencyHitTest.value ? isTransparentByThree.value : true

  if (stageModelRenderer.value === 'live2d')
    return isTransparentByPixels.value

  return true
})

const { isNearAnyBorder: isAroundWindowBorder } = useElectronMouseAroundWindowBorder({ threshold: 10 })
const isAroundWindowBorderFor250Ms = refDebounced(isAroundWindowBorder, 250)

const setIgnoreMouseEvents = useElectronEventaInvoke(electron.window.setIgnoreMouseEvents)

const live2dStore = useLive2d()
const { scale, positionInPercentageString } = storeToRefs(live2dStore)
const { live2dLookAtX, live2dLookAtY } = storeToRefs(useWindowStore())

const { pause, resume } = watch(isTransparent, (transparent) => {
  shouldFadeOnCursorWithin.value = fadeOnHoverEnabled.value && !transparent
}, { immediate: true })

const hearingDialogOpen = computed(() => controlsIslandRef.value?.hearingDialogOpen ?? false)

const modelSettingsRuntimeSnapshot = computed<ModelSettingsRuntimeSnapshot>(() => {
  const hasModel = !!stageModelSelectedUrl.value

  if (stageModelRenderer.value === 'live2d') {
    const phase = resolveComponentStateToRuntimePhase(componentStateStage.value, { hasModel })

    return createEmptyModelSettingsRuntimeSnapshot({
      ownerInstanceId: modelSettingsRuntimeOwnerInstanceId,
      renderer: 'live2d',
      phase,
      controlsLocked: hasModel ? phase !== 'mounted' : false,
      previewAvailable: hasModel,
      canCapturePreview: false,
      updatedAt: Date.now(),
    })
  }

  if (stageModelRenderer.value === 'vrm') {
    return createEmptyModelSettingsRuntimeSnapshot({
      ownerInstanceId: modelSettingsRuntimeOwnerInstanceId,
      renderer: 'vrm',
      phase: hasModel ? scenePhase.value : 'no-model',
      controlsLocked: hasModel
        ? (!stageMounted.value || sceneMutationLocked.value)
        : false,
      previewAvailable: hasModel,
      canCapturePreview: false,
      updatedAt: Date.now(),
    })
  }

  if (stageModelRenderer.value === 'godot') {
    return createEmptyModelSettingsRuntimeSnapshot({
      ownerInstanceId: modelSettingsRuntimeOwnerInstanceId,
      renderer: 'godot',
      phase: hasModel ? 'mounted' : 'no-model',
      controlsLocked: false,
      previewAvailable: false,
      canCapturePreview: false,
      updatedAt: Date.now(),
    })
  }

  return createEmptyModelSettingsRuntimeSnapshot({
    ownerInstanceId: modelSettingsRuntimeOwnerInstanceId,
    updatedAt: Date.now(),
  })
})

watch([isOutsideFor250Ms, isOutsideStatusIslandFor250Ms, isAroundWindowBorderFor250Ms, isOutsideWindow, isTransparent, hearingDialogOpen, fadeOnHoverEnabled, stagePaused], () => {
  if (stagePaused.value) {
    isIgnoringMouseEvents.value = false
    shouldFadeOnCursorWithin.value = false
    setIgnoreMouseEvents([false, { forward: true }])
    pause()
    return
  }

  if (hearingDialogOpen.value) {
    // Hearing dialog/drawer is open; keep window interactive
    isIgnoringMouseEvents.value = false
    shouldFadeOnCursorWithin.value = false
    setIgnoreMouseEvents([false, { forward: true }])
    pause()
    return
  }

  const insideControls = !isOutsideFor250Ms.value || !isOutsideStatusIslandFor250Ms.value
  const nearBorder = isAroundWindowBorderFor250Ms.value

  if (insideControls || nearBorder) {
    // Inside interactive controls or near resize border: do NOT ignore events
    isIgnoringMouseEvents.value = false
    shouldFadeOnCursorWithin.value = false
    setIgnoreMouseEvents([false, { forward: true }])
    pause()
  }
  else {
    const fadeEnabled = fadeOnHoverEnabled.value
    // Otherwise allow click-through while we fade UI based on transparency (when enabled)
    isIgnoringMouseEvents.value = fadeEnabled
    shouldFadeOnCursorWithin.value = fadeEnabled && !isOutsideWindow.value && !isTransparent.value
    setIgnoreMouseEvents([fadeEnabled, { forward: true }])
    if (fadeEnabled)
      resume()
    else
      pause()
  }
})

// Emit runtime snapshot on change and on request from settings panel
watch(modelSettingsRuntimeSnapshot, (snapshot) => {
  postModelSettingsRuntimeChannelEvent({ type: 'snapshot', snapshot })
}, { immediate: true })

watch(modelSettingsRuntimeChannelEvent, (event) => {
  if (event?.type !== 'request-current')
    return

  postModelSettingsRuntimeChannelEvent({ type: 'snapshot', snapshot: modelSettingsRuntimeSnapshot.value })
})

const settingsAudioDeviceStore = useSettingsAudioDevice()
const { stream, enabled } = storeToRefs(settingsAudioDeviceStore)
const { askPermission } = settingsAudioDeviceStore
const { startRecord, stopRecord, onStopRecord } = useAudioRecorder(stream)
const hearingPipeline = useHearingSpeechInputPipeline()
const { transcribeForRecording, transcribeForMediaStream, stopStreamingTranscription } = hearingPipeline
const { supportsStreamInput } = storeToRefs(hearingPipeline)
const chatSyncStore = useChatSyncStore()
const shouldUseStreamInput = computed(() => supportsStreamInput.value && !!stream.value)

const { init: initVAD, dispose: disposeVAD, start: startVAD, loaded: vadLoaded } = useVAD(workletUrl, {
  threshold: ref(0.6),
  onSpeechStart: () => {
    void handleSpeechStart()
  },
  onSpeechEnd: () => {
    void handleSpeechEnd()
  },
})

let stopOnStopRecord: (() => void) | undefined
const audioInteractionStarting = ref(false)

// Caption overlay broadcast channel
type CaptionChannelEvent
  = | { type: 'caption-speaker', text: string }
    | { type: 'caption-assistant', text: string }
const { post: postCaption } = useBroadcastChannel<CaptionChannelEvent, CaptionChannelEvent>({ name: 'airi-caption-overlay' })
const lastBridgeAssistantCaption = ref('')
const lastBridgeAssistantTimestamp = ref(0)
let bridgeCaptionTimer: ReturnType<typeof setInterval> | undefined
let bridgeEventSync: ReturnType<typeof createXiaomiaoBridgeEventSync> | undefined
const handledStageActionEventIds = new Set<number>()

// NOTICE:
// The current QQ ↔ desktop integration is bound to the active XiaoMiao owner QQ.
// Root cause: the desktop bridge does not yet expose a user binding handshake to the renderer.
// Source/context: `xiaomiao/config.json` currently runs with a single owner identity during integration testing.
// Removal condition: replace with renderer-side binding state once multi-user session mapping lands.
const BOUND_XIAOMIAO_USER_ID = 3554978979

async function pollXiaomiaoBridgeCaption() {
  try {
    const bridgeState = await readXiaomiaoBridgeState(fetch, BOUND_XIAOMIAO_USER_ID)
    if (!bridgeState) {
      return
    }

    const reactionResult = await applyXiaomiaoBridgeReaction({
      currentTimestamp: lastBridgeAssistantTimestamp.value,
      currentText: lastBridgeAssistantCaption.value,
      bridgeState,
      postCaption: text => postCaption({ type: 'caption-assistant', text }),
      syncChatHistory: () => {},
      ensureSpeechReady: ensureBridgeSpeechReady,
      speakReply: async text => await characterStore.emitTextOutput(text),
    })

    if (!reactionResult.accepted) {
      return
    }

    lastBridgeAssistantCaption.value = reactionResult.nextText
    lastBridgeAssistantTimestamp.value = reactionResult.nextTimestamp
  }
  catch {
    // Ignore local bridge polling errors so the stage keeps rendering normally.
  }
}

function startBridgeEventSync() {
  bridgeEventSync = createXiaomiaoBridgeEventSync({
    getMessages: () => chatSession.getSessionMessages(chatSession.activeSessionId),
    setMessages: messages => chatSession.setSessionMessages(chatSession.activeSessionId, messages),
    logger: { error: () => {} },
    onEvents: async (events) => {
      await applyXiaomiaoStageActionEvents({
        events,
        handledEventIds: handledStageActionEventIds,
        postCaption: text => postCaption({ type: 'caption-assistant', text }),
        ensureSpeechReady: ensureBridgeSpeechReady,
        speakReply: async text => await characterStore.emitTextOutput(text),
        applyEmotion: applyStageEmotion,
        applyBackground: applyStageBackground,
        applyModel: applyStageModel,
        readStatus: readStageStatus,
        onRejected: appendStageActionError,
      })
    },
  })
  bridgeEventSync.start()
}

function stopBridgeEventSync() {
  bridgeEventSync?.stop()
  bridgeEventSync = undefined
}

async function applyStageEmotion(name: string, intensity: number) {
  const normalized = name.trim().toLowerCase()
  if (!EMOTION_VALUES.includes(normalized as (typeof EMOTION_VALUES)[number]))
    throw new Error(`未知表情：${name}`)

  await characterStore.emitTextOutput(`<|ACT ${JSON.stringify({ emotion: { name: normalized, intensity } })}|>`)
}

async function applyStageBackground(id: string) {
  const backgroundId = id.trim()
  if (!backgroundId)
    throw new Error('背景 ID 不能为空')

  if (backgroundId !== 'none') {
    await backgroundStore.initializeStore()
    if (!backgroundStore.entries.has(backgroundId))
      throw new Error(`背景不存在：${backgroundId}`)
  }

  const cardId = airiCardStore.activeCardId
  const card = airiCardStore.activeCard
  if (!card || !cardId)
    throw new Error('当前没有可写入的角色卡')

  const extensions = JSON.parse(JSON.stringify(card.extensions || {}))
  if (!extensions.airi)
    extensions.airi = {}
  if (!extensions.airi.modules)
    extensions.airi.modules = {}
  extensions.airi.modules.activeBackgroundId = backgroundId

  const updated = {
    ...card,
    extensions,
  }
  if (!airiCardStore.updateCard(cardId, updated))
    throw new Error(`更新角色卡背景失败：${cardId}`)
}

async function applyStageModel(id: string) {
  const modelId = id.trim()
  if (!modelId)
    throw new Error('模型 ID 不能为空')

  const model = await displayModelsStore.getDisplayModel(modelId)
  if (!model)
    throw new Error(`模型不存在：${modelId}`)

  settingsStore.stageModelSelected = modelId
  await settingsStore.updateStageModel()

  const cardId = airiCardStore.activeCardId
  const card = airiCardStore.activeCard
  if (!card || !cardId)
    return

  const extensions = JSON.parse(JSON.stringify(card.extensions || {}))
  if (!extensions.airi)
    extensions.airi = {}
  if (!extensions.airi.modules)
    extensions.airi.modules = {}
  extensions.airi.modules.displayModelId = modelId
  airiCardStore.updateCard(cardId, { ...card, extensions })
}

function readStageStatus(query?: string) {
  const activeBackgroundId = airiCardStore.activeCard?.extensions?.airi?.modules?.activeBackgroundId || 'none'
  const modelName = settingsStore.stageModelSelectedDisplayModel?.name || settingsStore.stageModelSelected || 'none'
  const recentMessage = chatSession.getSessionMessages(chatSession.activeSessionId)
    .filter(message => message.role !== 'system')
    .at(-1)
    ?.content
  const recent = typeof recentMessage === 'string' && recentMessage.trim()
    ? truncateStatusText(recentMessage.trim())
    : 'none'

  return [
    `舞台在线：${stageMounted.value ? 'yes' : 'loading'}`,
    `查询：${query || 'current'}`,
    `角色：${airiCardStore.activeCard?.name || 'unknown'}`,
    `模型：${modelName}`,
    `渲染器：${settingsStore.stageModelRenderer || 'disabled'}`,
    `背景：${activeBackgroundId}`,
    `语音：${speechStore.activeSpeechProvider || 'none'}/${speechStore.activeSpeechModel || 'none'}/${speechStore.activeSpeechVoiceId || 'none'}`,
    `最近消息：${recent}`,
  ].join('\n')
}

function appendStageActionError(rejection: XiaomiaoStageActionRejection) {
  const content = `[舞台动作失败${rejection.action ? `:${rejection.action}` : ''}] ${rejection.reason}`
  postCaption({ type: 'caption-assistant', text: content })
  if (!chatSession.activeSessionId)
    return

  chatSession.appendSessionMessage(chatSession.activeSessionId, {
    id: `xiaomiao-stage-action-error-${rejection.id}`,
    role: 'error',
    content,
    createdAt: Date.now(),
  } as ChatHistoryItem)
}

function truncateStatusText(text: string) {
  return text.length > 80 ? `${text.slice(0, 77)}...` : text
}

function handleStreamingSentenceEnd(delta: string) {
  console.info('[Main Page] Received transcription delta:', delta)
  const finalText = delta
  if (!finalText || !finalText.trim()) {
    return
  }

  postCaption({ type: 'caption-speaker', text: finalText })

  void (async () => {
    try {
      console.info('[Main Page] Sending transcription to chat:', finalText)
      await chatSyncStore.requestIngest({ text: finalText })
    }
    catch (err) {
      console.error('[Main Page] Failed to send chat from voice:', err)
    }
  })()
}

function handleStreamingSpeechEnd(text: string) {
  console.info('[Main Page] Speech ended, final text:', text)
  postCaption({ type: 'caption-speaker', text })
}

async function handleSpeechStart() {
  if (shouldUseStreamInput.value) {
    console.info('Speech detected - transcription session should already be active')
    return
  }

  startRecord()
}

async function handleSpeechEnd() {
  if (shouldUseStreamInput.value) {
    // Keep streaming session alive; idle timer in pipeline will handle teardown.
    return
  }

  stopRecord()
}

async function startAudioInteraction() {
  if (audioInteractionStarting.value)
    return

  // NOTICE: `stopOnStopRecord` only tracks whether the non-stream recording hook was registered.
  //
  // It does NOT guarantee that the current realtime transcription session is still attached to the
  // latest `MediaStream`. We previously used it as a generic "already started" guard, which broke
  // the hearing-config retoggle path: the mic stream was recreated, VAD restarted on the new stream,
  // but `transcribeForMediaStream()` never reattached so speech was detected without any transcript.
  //
  // Keep the startup guard scoped to "startup in progress" only, and let stream changes restart the
  // transcription binding when a new stream arrives.
  audioInteractionStarting.value = true
  try {
    console.info('[Main Page] Starting audio interaction...')

    initVAD().then(() => {
      if (stream.value) {
        console.info('[Main Page] VAD initialized successfully, starting with stream input')
        return startVAD(stream.value)
      }
    }).catch((err) => {
      console.warn('[Main Page] VAD initialization failed (non-critical for Web Speech API):', err)
    })

    if (shouldUseStreamInput.value) {
      console.info('[Main Page] Starting streaming transcription...', {
        supportsStreamInput: supportsStreamInput.value,
        hasStream: !!stream.value,
      })

      if (!stream.value) {
        console.warn('[Main Page] Stream not available despite shouldUseStreamInput being true')
        return
      }

      // Use sentence deltas for live captions and speech end for final text.
      await transcribeForMediaStream(stream.value, {
        onSentenceEnd: handleStreamingSentenceEnd,
        onSpeechEnd: handleStreamingSpeechEnd,
      })

      console.info('[Main Page] Streaming transcription started successfully')
    }
    else {
      console.warn('[Main Page] Not starting streaming transcription:', {
        shouldUseStreamInput: shouldUseStreamInput.value,
        hasStream: !!stream.value,
        supportsStreamInput: supportsStreamInput.value,
      })
    }

    // NOTICE: This hook is only for record-then-transcribe providers.
    //
    // Streaming providers use the active `MediaStream` directly, so this callback must not be treated
    // as proof that a realtime session is alive. Future refactors should keep recorder-hook bookkeeping
    // separate from stream transcription state, otherwise mic/device re-toggles can leave VAD active
    // but transcription detached.
    //
    // Hook once for non-streaming providers.
    if (!stopOnStopRecord) {
      stopOnStopRecord = onStopRecord(async (recording) => {
        if (shouldUseStreamInput.value)
          return

        const text = await transcribeForRecording(recording)
        if (!text || !text.trim())
          return

        // Update caption overlay speaker text via BroadcastChannel
        postCaption({ type: 'caption-speaker', text })

        try {
          await chatSyncStore.requestIngest({ text })
        }
        catch (err) {
          console.error('Failed to send chat from voice:', err)
        }
      })
    }
  }
  catch (e) {
    console.error('Audio interaction init failed:', e)
  }
  finally {
    audioInteractionStarting.value = false
  }
}

function stopAudioInteraction() {
  tryCatch(() => {
    stopOnStopRecord?.()
    stopOnStopRecord = undefined
    audioInteractionStarting.value = false
    void stopStreamingTranscription(true)
    disposeVAD()
  })
}

watch(enabled, async (val) => {
  console.info('[Main Page] Audio enabled changed:', val, 'stream available:', !!stream.value)
  if (val) {
    await askPermission()
    await startAudioInteraction()
  }
  else {
    stopAudioInteraction()
  }
}, { immediate: true })

onMounted(() => {
  chatSyncStore.initialize('authority')
  void ensureBridgeSpeechReady()
  bridgeCaptionTimer = setInterval(() => {
    void pollXiaomiaoBridgeCaption()
  }, 1500)
  startBridgeEventSync()
  if (onboardingStore.needsOnboarding) {
    openOnboarding()
  }
})

onUnmounted(() => {
  if (bridgeCaptionTimer) {
    clearInterval(bridgeCaptionTimer)
    bridgeCaptionTimer = undefined
  }
  stopBridgeEventSync()
  postModelSettingsRuntimeChannelEvent({
    type: 'owner-gone',
    ownerInstanceId: modelSettingsRuntimeOwnerInstanceId,
  })
  stopAudioInteraction()
  chatSyncStore.dispose()
})

watch(stream, async (currentStream) => {
  if (!enabled.value || !currentStream || audioInteractionStarting.value)
    return

  // NOTICE: The controls-island mic toggle and device changes can replace the underlying MediaStream
  // without reloading the page. When that happens, VAD may successfully restart against the new stream,
  // but any existing transcription transport is still bound to the old one. Always allow the page to
  // re-run `startAudioInteraction()` for a newly available stream unless startup is already underway.
  console.info('[Main Page] Stream became available, ensuring audio interaction is started')
  await startAudioInteraction()
})

watch([stream, () => vadLoaded.value], async ([s, loaded]) => {
  if (enabled.value && loaded && s) {
    try {
      await startVAD(s)
    }
    catch (e) {
      console.error('Failed to start VAD with stream:', e)
    }
  }
})

// Assistant caption is broadcast from Stage.vue via the same channel
</script>

<template>
  <div
    max-h="[100vh]"
    max-w="[100vw]"
    flex="~ col"
    relative z-2 h-full overflow-hidden rounded-xl
    transition="opacity duration-500 ease-in-out"
  >
    <!-- Stage is always in DOM so TresCanvas can measure dimensions -->
    <div
      :class="[
        'relative h-full w-full items-end gap-2',
        'transition-opacity duration-250 ease-in-out',
      ]"
    >
      <div
        :class="[
          shouldFadeOnCursorWithin ? 'op-0' : 'op-100',
          'absolute',
          'top-0 left-0 w-full h-full',
          'overflow-hidden',
          'rounded-2xl',
          'transition-opacity duration-250 ease-in-out',
        ]"
      >
        <StatusIsland ref="statusIslandRef" />
        <ResourceStatusIsland />
        <WidgetStage
          ref="widgetStageRef"
          v-model:state="componentStateStage"
          h-full w-full
          flex-1
          :paused="stagePaused"
          :focus-at="{ x: live2dLookAtX, y: live2dLookAtY }"
          :scale="scale"
          :x-offset="positionInPercentageString.x"
          :y-offset="positionInPercentageString.y"
        />
        <HoloCoupon />
        <ControlsIsland
          ref="controlsIslandRef"
        />
      </div>
    </div>
    <!-- Loading overlay sits on top, does not hide the stage -->
    <div v-show="isLoading" class="absolute left-0 top-0 z-99 h-full w-full flex cursor-grab items-center justify-center overflow-hidden">
      <div
        :class="[
          'absolute h-24 w-full overflow-hidden rounded-xl',
          'flex items-center justify-center',
          'bg-white/80 dark:bg-neutral-950/80',
          'backdrop-blur-md',
        ]"
      >
        <div
          :class="[
            'drag-region',
            'absolute left-0 top-0',
            'h-full w-full flex items-center justify-center',
            'text-1.5rem text-primary-600 dark:text-primary-400 font-normal',
            'select-none',
            'animate-flash animate-duration-5s animate-count-infinite',
          ]"
        >
          Loading...
        </div>
      </div>
    </div>
  </div>
  <Transition
    enter-active-class="transition-opacity duration-250"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-250"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="false"
      class="absolute left-0 top-0 z-99 h-full w-full flex cursor-grab items-center justify-center overflow-hidden drag-region"
    >
      <div
        class="absolute h-32 w-full flex items-center justify-center overflow-hidden rounded-xl"
        bg="white/80 dark:neutral-950/80" backdrop-blur="md"
      >
        <div class="wall absolute top-0 h-8" />
        <div class="absolute left-0 top-0 h-full w-full flex animate-flash animate-duration-5s animate-count-infinite select-none items-center justify-center text-1.5rem text-primary-400 font-normal drag-region">
          DRAG HERE TO MOVE
        </div>
        <div class="wall absolute bottom-0 h-8 drag-region" />
      </div>
    </div>
  </Transition>
  <Transition
    enter-active-class="transition-opacity duration-250 ease-in-out"
    enter-from-class="opacity-50"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-250 ease-in-out"
    leave-from-class="opacity-100"
    leave-to-class="opacity-50"
  >
    <div v-if="isAroundWindowBorderFor250Ms && !isLoading" class="pointer-events-none absolute left-0 top-0 z-999 h-full w-full">
      <div
        :class="[
          'b-primary/50',
          'h-full w-full animate-flash animate-duration-3s animate-count-infinite b-4 rounded-2xl',
        ]"
      />
    </div>
  </Transition>
</template>

<style scoped>
@keyframes wall-move {
  0% {
    transform: translateX(calc(var(--wall-width) * -2));
  }
  100% {
    transform: translateX(calc(var(--wall-width) * 1));
  }
}

.wall {
  --at-apply: text-primary-300;

  --wall-width: 8px;
  animation: wall-move 1s linear infinite;
  background-image: repeating-linear-gradient(
    45deg,
    currentColor,
    currentColor var(--wall-width),
    #ff00 var(--wall-width),
    #ff00 calc(var(--wall-width) * 2)
  );
  width: calc(100% + 4 * var(--wall-width));
}
</style>

<route lang="yaml">
meta:
  layout: stage
</route>
