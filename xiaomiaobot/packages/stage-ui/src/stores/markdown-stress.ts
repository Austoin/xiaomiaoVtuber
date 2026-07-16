import type { TraceEvent } from '@proj-airi/stage-shared'

import { defaultPerfTracer, exportCsv as exportCsvFile } from '@proj-airi/stage-shared'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { useChatOrchestratorStore } from './chat'
import { usePerfTracerBridgeStore } from './perf-tracer-bridge'

interface RunSnapshot {
  startedAt: number
  stoppedAt: number
  events: TraceEvent[]
}

interface DevtoolsChatScenario {
  userMessages: Array<{ atMs: number, text: string }>
  assistant: {
    text: string
    firstTokenDelayMs?: number
    rate?: {
      tokensPerSecond?: number
      jitterMs?: number
      maxChunkSize?: number
    }
  }
}

export const useMarkdownStressStore = defineStore('markdownStress', () => {
  const capturing = ref(false)
  const events = ref<TraceEvent[]>([])
  const lastRun = ref<RunSnapshot>()
  const payloadPreview = ref<string>('')
  const scheduleDelayMs = ref(10000)
  const runState = ref<'idle' | 'scheduled' | 'running'>('idle')
  const scenario = ref<DevtoolsChatScenario | null>(null)
  const isMock = ref(false)
  const canRunOnline = ref(true)
  const perfTracerBridge = usePerfTracerBridgeStore()

  let unsubscribe: (() => void) | undefined
  let startedAt = 0
  let releaseTracer: (() => void) | undefined
  let runTimeout: ReturnType<typeof setTimeout> | undefined
  let autoStopTimeout: ReturnType<typeof setTimeout> | undefined
  let inFlightTimers: Array<ReturnType<typeof setTimeout>> = []

  function clearTimers() {
    if (runTimeout) {
      clearTimeout(runTimeout)
      runTimeout = undefined
    }
    if (autoStopTimeout) {
      clearTimeout(autoStopTimeout)
      autoStopTimeout = undefined
    }
    for (const timer of inFlightTimers)
      clearTimeout(timer)
    inFlightTimers = []
  }

  function startCapture() {
    if (capturing.value)
      return

    capturing.value = true
    startedAt = performance.now()
    events.value = []

    unsubscribe = defaultPerfTracer.subscribeSafe((event) => {
      if (event.tracerId !== 'markdown' && event.tracerId !== 'chat')
        return

      events.value.push(event)
    }, { label: 'markdown-stress' })
    releaseTracer = defaultPerfTracer.acquire('markdown-stress')
    perfTracerBridge.requestEnable('markdown-stress')
  }

  function stopCapture() {
    if (!capturing.value)
      return

    clearTimers()
    lastRun.value = {
      startedAt,
      stoppedAt: performance.now(),
      events: [...events.value],
    }

    unsubscribe?.()
    unsubscribe = undefined
    releaseTracer?.()
    releaseTracer = undefined
    perfTracerBridge.requestDisable('markdown-stress')
    capturing.value = false
    runState.value = 'idle'
  }

  function buildForFlood() {
    const line = 'for for for for for'
    // 800 lines * 5 words = 4000 tokens
    return Array.from({ length: 800 }).fill(line).join('\n')
  }

  function generateScenario(): DevtoolsChatScenario {
    const userPrompt = 'Give me a huge stress-test JavaScript block with 2000 occurrences of the keyword `for` wrapped in ```javascript```.'
    const followUp = 'I really need a JS block containing 2000 `for` keywords — please ensure the request is fully satisfied.'
    const assistantText = [
      'Here is a large JS `for` block (line breaks every 5 entries, about 4000 words total):',
      '```python',
      buildForFlood(),
      '```',
      'Done. This should heavily stress markdown parsing and rendering.',
    ].join('\n\n')

    return {
      userMessages: [
        { atMs: 0, text: userPrompt },
        { atMs: 1200, text: followUp },
      ],
      assistant: {
        text: assistantText,
        firstTokenDelayMs: 150,
        rate: { tokensPerSecond: 120, jitterMs: 5, maxChunkSize: 96 },
      },
    }
  }

  function ensureScenario() {
    if (!scenario.value)
      scenario.value = generateScenario()
    return scenario.value
  }

  function generatePreview() {
    const next = generateScenario()
    scenario.value = next
    payloadPreview.value = [
      `User (t=0ms): ${next.userMessages[0].text}`,
      `User (t=${next.userMessages[1].atMs}ms): ${next.userMessages[1].text}`,
      '--- Assistant stream ---',
      next.assistant.text,
    ].join('\n\n')
  }

  async function runOnlineScenario() {
    const chatStore = useChatOrchestratorStore()
    const targetScenario = ensureScenario()
    canRunOnline.value = true

    const runStart = performance.now()
    for (const message of targetScenario.userMessages) {
      const delay = Math.max(0, runStart + message.atMs - performance.now())
      const timer = setTimeout(async () => {
        try {
          await chatStore.ingest(message.text, {})
        }
        catch (error) {
          console.error('[markdown-stress] Online send failed', error)
        }
      }, delay)
      inFlightTimers.push(timer)
    }
  }

  async function runMockScenario() {
    await runOnlineScenario()
  }

  async function scheduleRun() {
    // if already scheduled, cancel
    if (runState.value === 'scheduled') {
      cancelScheduledRun()
      return
    }

    // if already running, abort immediately
    if (runState.value === 'running') {
      stopCapture()
      return
    }

    clearTimers()
    ensureScenario()
    runState.value = 'scheduled'

    runTimeout = setTimeout(async () => {
      runState.value = 'running'
      runTimeout = undefined
      startCapture()
      if (isMock.value)
        await runMockScenario()
      else
        await runOnlineScenario()
    }, scheduleDelayMs.value)

    autoStopTimeout = setTimeout(() => {
      stopCapture()
    }, scheduleDelayMs.value + 60000)
  }

  function cancelScheduledRun() {
    clearTimers()
    runState.value = 'idle'
  }

  function setMockMode(enabled: boolean) {
    isMock.value = enabled
    if (enabled)
      canRunOnline.value = true
  }

  function toggleMockMode() {
    setMockMode(!isMock.value)
  }

  function exportCsv(snapshot?: RunSnapshot) {
    const target = snapshot ?? lastRun.value
    if (!target)
      return

    const rows: Array<Array<string | number>> = [['tracerId', 'name', 'ts', 'duration', 'meta']]
    for (const event of target.events) {
      rows.push([
        event.tracerId,
        event.name,
        event.ts.toFixed(3),
        event.duration ?? '',
        JSON.stringify(event.meta ?? {}),
      ])
    }

    exportCsvFile(rows, 'markdown-stress')
  }

  return {
    canRunOnline,
    capturing,
    events,
    lastRun,
    payloadPreview,
    scheduleDelayMs,
    runState,
    scenario,
    isMock,
    startCapture,
    stopCapture,
    scheduleRun,
    cancelScheduledRun,
    generatePreview,
    setMockMode,
    toggleMockMode,
    exportCsv,
  }
})
