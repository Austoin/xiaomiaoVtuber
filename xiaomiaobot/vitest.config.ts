import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    maxWorkers: 4,
    projects: [
      'apps/stage-pocket',
      'apps/stage-tamagotchi',
      'packages/audio-pipelines-transcribe',
      'packages/cap-vite',
      'packages/vishot-runner-browser',
      'packages/plugin-sdk',
      'packages/plugin-sdk-tamagotchi',
      'packages/server-runtime',
      'packages/server-sdk',
      'packages/stage-layouts',
      'packages/stage-shared',
      'packages/stage-ui/vitest.config.ts',
      'packages/stage-ui/vitest.browser.config.ts',
      'packages/vishot-runtime',
      'packages/vite-plugin-warpdrive',
    ],
  },
})
