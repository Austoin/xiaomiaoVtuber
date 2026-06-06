import type { ChatHistoryItem } from '@proj-airi/stage-ui/types/chat'
import type {
  XiaomiaoBridgeEventsRequest,
  XiaomiaoBridgeEventsResult,
} from '@proj-airi/stage-layouts/xiaomiao-bridge'

import {
  appendXiaomiaoBridgeEvents,
  requestXiaomiaoBridgeEvents,
} from '@proj-airi/stage-layouts/xiaomiao-bridge'

export const STAGE_POCKET_BRIDGE_EVENTS_POLL_INTERVAL_MS = 1500

type RequestBridgeEvents = (params?: XiaomiaoBridgeEventsRequest) => Promise<XiaomiaoBridgeEventsResult>
type TimerHandle = ReturnType<typeof setInterval>

export interface StagePocketBridgeEventSyncOptions {
  getMessages: () => ChatHistoryItem[]
  setMessages: (messages: ChatHistoryItem[]) => void
  requestEvents?: RequestBridgeEvents
  pollIntervalMs?: number
  includeWeb?: boolean
  setIntervalFn?: typeof setInterval
  clearIntervalFn?: typeof clearInterval
  logger?: Pick<Console, 'error'>
}

export interface StagePocketBridgeEventSync {
  poll: () => Promise<void>
  start: () => void
  stop: () => void
  getCursor: () => number
  isRunning: () => boolean
}

export function createStagePocketBridgeEventSync(
  options: StagePocketBridgeEventSyncOptions,
): StagePocketBridgeEventSync {
  const requestEvents = options.requestEvents ?? requestXiaomiaoBridgeEvents
  const pollIntervalMs = options.pollIntervalMs ?? STAGE_POCKET_BRIDGE_EVENTS_POLL_INTERVAL_MS
  const setIntervalFn = options.setIntervalFn ?? setInterval
  const clearIntervalFn = options.clearIntervalFn ?? clearInterval
  const logger = options.logger ?? console
  const includeWeb = options.includeWeb ?? true

  let cursor = 0
  let polling = false
  let timer: TimerHandle | undefined

  async function poll(): Promise<void> {
    if (polling)
      return

    polling = true
    try {
      const result = await requestEvents({ after: cursor })
      cursor = Math.max(cursor, result.lastId)

      const currentMessages = options.getMessages()
      const nextMessages = appendXiaomiaoBridgeEvents(
        currentMessages,
        result.events,
        { includeWeb },
      )

      if (nextMessages !== currentMessages)
        options.setMessages(nextMessages)
    }
    catch (error) {
      logger.error('Failed to sync XiaoMiao bridge events in stage-pocket:', error)
    }
    finally {
      polling = false
    }
  }

  function start(): void {
    if (timer !== undefined)
      return

    void poll()
    timer = setIntervalFn(() => {
      void poll()
    }, pollIntervalMs)
  }

  function stop(): void {
    if (timer === undefined)
      return

    clearIntervalFn(timer)
    timer = undefined
  }

  return {
    poll,
    start,
    stop,
    getCursor: () => cursor,
    isRunning: () => timer !== undefined,
  }
}
