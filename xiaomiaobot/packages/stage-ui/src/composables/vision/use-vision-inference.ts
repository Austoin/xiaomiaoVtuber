import type { VisionWorkloadId } from './use-vision-workloads'

import { ref } from 'vue'

import { requestXiaomiaoAgentReply } from '../../libs/xiaomiao-agent'
import { getVisionWorkload } from './use-vision-workloads'

export interface VisionInferenceInput {
  imageDataUrl: string
  workloadId: VisionWorkloadId
  promptOverride?: string
}

// TODO: this should be configurable
const VISION_INFERENCE_TIMEOUT_MS = 60_000

function parseDataUrl(dataUrl: string) {
  if (!dataUrl.startsWith('data:'))
    return { mimeType: 'image/png', base64: dataUrl, url: dataUrl }

  const [, meta, data] = dataUrl.match(/^data:([^,]+),(.*)$/) || []
  const mimeType = meta?.split(';')[0] || 'image/png'
  const base64 = meta?.includes('base64') ? data : btoa(data)
  return {
    mimeType,
    base64,
    url: `data:${mimeType};base64,${base64}`,
  }
}

export function useVisionInference() {
  const lastText = ref('')

  async function runVisionInference(input: VisionInferenceInput) {
    const workload = getVisionWorkload(input.workloadId)
    const prompt = input.promptOverride ?? workload.prompt
    const { url } = parseDataUrl(input.imageDataUrl)
    const abortController = new AbortController()
    const timeoutHandle = setTimeout(() => {
      abortController.abort(new Error(`Vision inference timed out after ${VISION_INFERENCE_TIMEOUT_MS}ms`))
    }, VISION_INFERENCE_TIMEOUT_MS)

    try {
      lastText.value = await requestXiaomiaoAgentReply({
        text: prompt,
        media: [url],
        clientMessageId: `stage-vision-${Date.now().toString(36)}`,
        signal: abortController.signal,
      })
    }
    catch (error) {
      if (abortController.signal.aborted) {
        throw abortController.signal.reason instanceof Error
          ? abortController.signal.reason
          : new Error(`Vision inference timed out after ${VISION_INFERENCE_TIMEOUT_MS}ms`)
      }
      throw error
    }
    finally {
      clearTimeout(timeoutHandle)
    }

    return lastText.value
  }

  return {
    lastText,
    runVisionInference,
  }
}
