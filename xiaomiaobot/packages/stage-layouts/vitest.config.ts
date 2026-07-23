import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    name: '@proj-airi/stage-layouts',
    include: ['src/**/*.test.ts'],
  },
})
