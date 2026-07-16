import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const currentDirectory = dirname(fileURLToPath(import.meta.url))
const stageUiSource = resolve(currentDirectory, '../..')
const stagePagesSource = resolve(currentDirectory, '../../../../stage-pages/src')

function read(path: string) {
  return readFileSync(path, 'utf8')
}

describe('minecraft game companion integration contract', () => {
  it('keeps the settings page and public exports wired', () => {
    const modulesList = read(resolve(stageUiSource, 'composables/use-modules-list.ts'))
    const dataMaintenance = read(resolve(stageUiSource, 'composables/use-data-maintenance.ts'))
    const componentExports = read(resolve(stageUiSource, 'components/modules/index.ts'))
    const storeExports = read(resolve(stageUiSource, 'stores/modules/index.ts'))
    const settingsPage = read(resolve(stagePagesSource, 'pages/settings/modules/gaming-minecraft.vue'))

    expect(modulesList).toContain('id: \'gaming-minecraft\'')
    expect(modulesList).toContain('to: \'/settings/modules/gaming-minecraft\'')
    expect(dataMaintenance).toContain('minecraftStore.resetState()')
    expect(componentExports).toContain('export { default as GamingMinecraft } from \'./GamingMinecraft.vue\'')
    expect(storeExports).toContain('export * from \'./gaming-minecraft\'')
    expect(settingsPage).toContain('<GamingMinecraft />')
  })

  it('injects Minecraft context while keeping xiaomiaoAgent as the only inference layer', () => {
    const chatSource = read(resolve(stageUiSource, 'stores/chat.ts'))
    const contextProvider = read(resolve(stageUiSource, 'stores/chat/context-providers/minecraft.ts'))
    const minecraftStore = read(resolve(stageUiSource, 'stores/modules/gaming-minecraft.ts'))
    const recoveredSource = `${chatSource}\n${contextProvider}\n${minecraftStore}`

    expect(chatSource).toContain('createMinecraftContext()')
    expect(chatSource).toContain('requestXiaomiaoAgentReply')
    expect(recoveredSource).not.toMatch(/\b(?:generateText|streamText)\s*\(/)
  })
})
