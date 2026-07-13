import type { ArtifactTransformer, VishotArtifact } from '@proj-airi/vishot-runtime/runtime/artifact-types'
import type { ElectronApplication, Page } from 'playwright'

import type { StageWindowName, StageWindowSnapshot } from '../utils/windows'

export type { ArtifactTransformer, VishotArtifact, VishotArtifactKind, VishotArtifactStage } from '@proj-airi/vishot-runtime/runtime/artifact-types'

export interface CaptureOptions {
  fullPage?: boolean
  transformers?: ArtifactTransformer[]
}

export interface StageWindowsApi {
  waitFor: (name: StageWindowName, timeout?: number) => Promise<StageWindowSnapshot>
}

export interface ControlsIslandApi {
  waitForReady: (page: Page) => Promise<void>
  expand: (page: Page) => Promise<void>
  openSettings: (page: Page) => Promise<StageWindowSnapshot>
  openChat: (page: Page) => Promise<StageWindowSnapshot>
  openHearing: (page: Page) => Promise<Page>
}

export interface SettingsWindowApi {
  waitFor: (timeout?: number) => Promise<StageWindowSnapshot>
  goToConnection: (page: Page) => Promise<Page>
  goToRoute: (page: Page, routePath: string) => Promise<Page>
}

export interface DialogsApi {
  dismiss: (page: Page) => Promise<void>
}

export interface DrawersApi {
  swipeDown: (page: Page) => Promise<void>
  dismiss: (page: Page) => Promise<void>
}

export interface ScenarioContext {
  electronApp: ElectronApplication
  outputDir: string
  capture: (name: string, page: Page, options?: CaptureOptions) => Promise<VishotArtifact[]>
  stageWindows: StageWindowsApi
  controlsIsland: ControlsIslandApi
  settingsWindow: SettingsWindowApi
  dialogs: DialogsApi
  drawers: DrawersApi
}

export interface ElectronScenario {
  id: string
  run: (context: ScenarioContext) => Promise<void>
}
