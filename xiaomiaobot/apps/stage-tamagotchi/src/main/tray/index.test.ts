import { beforeAll, describe, expect, it, vi } from 'vitest'

vi.mock('electron', () => ({
  app: { quit: vi.fn() },
  Menu: { buildFromTemplate: vi.fn((template) => template) },
  Tray: vi.fn(),
  nativeImage: { createFromPath: vi.fn(() => ({ resize: vi.fn(() => ({ setTemplateImage: vi.fn() })) })) },
  screen: { getPrimaryDisplay: vi.fn(() => ({ workArea: { x: 0, y: 0, width: 1920, height: 1080 } })) },
}))

vi.mock('@electron-toolkit/utils', () => ({
  is: { dev: false },
}))

vi.mock('@proj-airi/electron-vueuse/main', () => ({
  isRendererUnavailable: vi.fn(() => false),
}))

vi.mock('alien-signals', () => ({
  effect: vi.fn(),
}))

vi.mock('../libs/bootkit/lifecycle', () => ({
  onAppBeforeQuit: vi.fn(),
}))

vi.mock('../windows/inlay', () => ({
  setupInlayWindow: vi.fn(),
}))

vi.mock('../windows/shared/window', () => ({
  toggleWindowShow: vi.fn(),
}))

vi.mock('../../../resources/icon.png?asset', () => ({ default: 'icon.png' }))
vi.mock('../../../resources/tray-icon-macos.png?asset', () => ({ default: 'tray-icon-macos.png' }))

let buildTrayMenuTemplate: typeof import('./index').buildTrayMenuTemplate
type TrayParams = Parameters<typeof import('./index').buildTrayMenuTemplate>[0]

beforeAll(async () => {
  ;({ buildTrayMenuTemplate } = await import('./index'))
})

function createWindowMock() {
  return {
    getBounds: vi.fn(() => ({ x: 0, y: 0, width: 450, height: 600 })),
  }
}

function createBaseParams() {
  return {
    mainWindow: createWindowMock(),
    settingsWindow: { openWindow: vi.fn() },
    widgetsWindow: { getWindow: vi.fn() },
    beatSyncBgWindow: { webContents: { openDevTools: vi.fn() } },
    aboutWindow: vi.fn(),
    serverChannel: {},
    i18n: {
      t: vi.fn((key: string) => key),
    },
  } as unknown as TrayParams
}

describe('buildTrayMenuTemplate', () => {
  it('includes caption actions when caption overlay is enabled', () => {
    const template = buildTrayMenuTemplate({
      ...createBaseParams(),
      captionWindow: {
        getWindow: vi.fn(),
        isVisible: vi.fn(() => false),
        getIsFollowingWindow: vi.fn(() => true),
        toggleVisibility: vi.fn(),
        toggleFollowWindow: vi.fn(),
        setFollowWindow: vi.fn(),
        resetToSide: vi.fn(),
        onVisibilityChanged: vi.fn(),
      },
    })

    const labels = template.flatMap((item) => {
      const own = 'label' in item && typeof item.label === 'string' ? [item.label] : []
      const nested = Array.isArray(item.submenu)
        ? item.submenu.flatMap((entry) => 'label' in entry && typeof entry.label === 'string' ? [entry.label] : [])
        : []
      return [...own, ...nested]
    })

    expect(labels).toContain('tamagotchi.electron.tray.menu.labels.label.open_caption')
    expect(labels).toContain('tamagotchi.electron.tray.menu.labels.label.caption_overlay')
  })

  it('switches caption into reset-position mode before repositioning', async () => {
    const captionWindow = {
      getWindow: vi.fn(),
      isVisible: vi.fn(() => false),
      getIsFollowingWindow: vi.fn(() => true),
      toggleVisibility: vi.fn(),
      toggleFollowWindow: vi.fn(),
      setFollowWindow: vi.fn(async () => {}),
      resetToSide: vi.fn(async () => {}),
      onVisibilityChanged: vi.fn(),
    }

    const template = buildTrayMenuTemplate({
      ...createBaseParams(),
      captionWindow,
    })

    const captionOverlay = template.find(item => 'label' in item && item.label === 'tamagotchi.electron.tray.menu.labels.label.caption_overlay')
    expect(captionOverlay && Array.isArray(captionOverlay.submenu)).toBe(true)

    const resetItem = (captionOverlay as { submenu: Array<{ label?: string, click?: () => Promise<void> }> }).submenu
      .find(item => item.label === 'tamagotchi.electron.tray.menu.labels.label.reset_position')

    expect(resetItem?.click).toBeTypeOf('function')
    await resetItem?.click?.()

    expect(captionWindow.setFollowWindow).toHaveBeenCalledWith(false)
    expect(captionWindow.resetToSide).toHaveBeenCalledTimes(1)
  })
})
