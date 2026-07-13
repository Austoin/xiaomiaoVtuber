import type {
  XiaomiaoBridgeEventSync,
  XiaomiaoBridgeEventSyncOptions,
} from '@proj-airi/stage-layouts/xiaomiao-bridge'

import {
  createXiaomiaoBridgeEventSync,
  XIAOMIAO_BRIDGE_EVENTS_POLL_INTERVAL_MS,
} from '@proj-airi/stage-layouts/xiaomiao-bridge'

export const STAGE_POCKET_BRIDGE_EVENTS_POLL_INTERVAL_MS = XIAOMIAO_BRIDGE_EVENTS_POLL_INTERVAL_MS

export type StagePocketBridgeEventSyncOptions = XiaomiaoBridgeEventSyncOptions
export type StagePocketBridgeEventSync = XiaomiaoBridgeEventSync

export function createStagePocketBridgeEventSync(
  options: StagePocketBridgeEventSyncOptions,
): StagePocketBridgeEventSync {
  return createXiaomiaoBridgeEventSync(options)
}
