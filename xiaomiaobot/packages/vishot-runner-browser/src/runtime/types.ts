import type { ArtifactTransformer } from '@proj-airi/vishot-runtime/runtime/artifact-types'

export interface CaptureBrowserCliArguments {
  renderEntry: string
  outputDir: string
  rootNames: string[]
}

export interface BrowserCaptureRequest {
  sceneAppRoot?: string
  baseUrl?: string
  routePath: string
  outputDir: string
  settleMs?: number
  rootNames?: string[]
  imageTransformers?: ArtifactTransformer[]
  viewport?: {
    width: number
    height: number
    deviceScaleFactor?: number
  }
}
export type { ArtifactTransformer, VishotArtifact, VishotArtifactKind, VishotArtifactStage } from '@proj-airi/vishot-runtime/runtime/artifact-types'
