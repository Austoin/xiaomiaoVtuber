import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const requestXiaomiaoAgentReply = vi.fn()

vi.mock('../../libs/xiaomiao-agent', () => ({
  requestXiaomiaoAgentReply,
}))

vi.mock('./use-vision-workloads', () => ({
  getVisionWorkload: () => ({
    prompt: 'Interpret this frame',
  }),
}))

describe('useVisionInference', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    requestXiaomiaoAgentReply.mockReset()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('passes an abort signal to xiaomiaoAgent', async () => {
    requestXiaomiaoAgentReply.mockImplementation(async (params) => {
      expect(params.signal).toBeInstanceOf(AbortSignal)
      return 'Frame summary'
    })

    const { useVisionInference } = await import('./use-vision-inference')
    const { runVisionInference } = useVisionInference()

    await expect(runVisionInference({
      imageDataUrl: 'data:image/png;base64,Zm9v',
      workloadId: 'screen:interpret',
    })).resolves.toBe('Frame summary')
  })

  it('aborts vision inference when the stream never settles', async () => {
    requestXiaomiaoAgentReply.mockImplementation(params => new Promise((_, reject) => {
      params.signal?.addEventListener('abort', () => {
        reject(params.signal?.reason)
      }, { once: true })
    }))

    const { useVisionInference } = await import('./use-vision-inference')
    const { runVisionInference } = useVisionInference()

    const result = runVisionInference({
      imageDataUrl: 'data:image/png;base64,Zm9v',
      workloadId: 'screen:interpret',
    })
    const expectation = expect(result).rejects.toThrow('Vision inference timed out after 60000ms')

    await vi.advanceTimersByTimeAsync(60_000)

    await expectation
  })
})
