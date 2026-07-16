import type { Message } from '@xsai/shared-chat'

export interface LLMConfig {
  apiUrl: string
  sessionId: string
}

export interface LLMCallOptions {
  messages: Message[]
  responseFormat?: { type: 'json_object' }
  reasoning?: { effort: 'low' | 'medium' | 'high' }
  abortSignal?: AbortSignal
  timeoutMs?: number
}

export interface LLMResult {
  text: string
  reasoning?: string
  // FIXME unsafe type
  usage: any
}

/**
 * Minecraft reasoning client backed by the single xiaomiaoAgent runtime.
 */
export class LLMAgent {
  constructor(private config: LLMConfig) { }

  private createLinkedAbortController(parentSignal?: AbortSignal): {
    controller: AbortController
    dispose: () => void
  } {
    const controller = new AbortController()
    if (!parentSignal) {
      return {
        controller,
        dispose: () => {},
      }
    }

    if (parentSignal.aborted) {
      controller.abort(parentSignal.reason)
      return {
        controller,
        dispose: () => {},
      }
    }

    const onAbort = () => {
      controller.abort(parentSignal.reason)
    }
    parentSignal.addEventListener('abort', onAbort, { once: true })
    return {
      controller,
      dispose: () => parentSignal.removeEventListener('abort', onAbort),
    }
  }

  /**
   * Call LLM with the given messages
   */
  async callLLM(options: LLMCallOptions): Promise<LLMResult> {
    const { controller, dispose } = this.createLinkedAbortController(options.abortSignal)
    const timeoutMs = typeof options.timeoutMs === 'number' && Number.isFinite(options.timeoutMs) && options.timeoutMs > 0
      ? Math.floor(options.timeoutMs)
      : null
    const timeoutError = timeoutMs
      ? Object.assign(new Error(`xiaomiaoAgent request timeout after ${timeoutMs}ms`), { name: 'TimeoutError' })
      : null
    const timeoutHandle = timeoutMs
      ? setTimeout(() => {
          if (!controller.signal.aborted)
            controller.abort(timeoutError)
        }, timeoutMs)
      : undefined

    try {
      const response = await fetch(this.config.apiUrl, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.config.sessionId,
          channel: 'minecraft',
          chat_id: 'minecraft-bot',
          user_id: 'minecraft-bot',
          messages: options.messages,
        }),
        signal: controller.signal,
      })
      if (!response.ok) {
        const detail = (await response.text()).trim()
        throw new Error(
          `xiaomiaoAgent request failed with HTTP ${response.status}${detail ? `: ${detail}` : ''}`,
        )
      }
      const payload = await response.json() as {
        choices?: Array<{ message?: { content?: string } }>
        usage?: unknown
      }

      return {
        text: payload.choices?.[0]?.message?.content ?? '',
        usage: payload.usage ?? {},
      }
    }
    finally {
      if (timeoutHandle)
        clearTimeout(timeoutHandle)
      dispose()
    }
  }
}
