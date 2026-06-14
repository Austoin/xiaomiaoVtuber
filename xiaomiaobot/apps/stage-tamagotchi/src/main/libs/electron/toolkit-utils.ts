/**
 * Replacement for @electron-toolkit/utils to avoid top-level electron.app access issues.
 *
 * NOTICE:
 * @electron-toolkit/utils v4.0.0 accesses electron.app.isPackaged at module top-level,
 * which fails when electron is externalized in CommonJS builds with Node.js v24+.
 * This module reimplements the needed functionality with delayed electron access.
 *
 * Source: @electron-toolkit/utils v4.0.0
 * https://github.com/alex8088/electron-toolkit/blob/main/packages/utils/src/index.ts
 */

import { app, session, type BrowserWindow } from 'electron'

export const is = {
  get dev() {
    return !app.isPackaged
  }
}

export const platform = {
  isWindows: process.platform === 'win32',
  isMacOS: process.platform === 'darwin',
  isLinux: process.platform === 'linux'
}

export const electronApp = {
  setAppUserModelId(id: string): void {
    if (platform.isWindows) {
      app.setAppUserModelId(is.dev ? process.execPath : id)
    }
  },
  setAutoLaunch(auto: boolean): boolean {
    if (platform.isLinux) return false

    const isOpenAtLogin = (): boolean => {
      return app.getLoginItemSettings().openAtLogin
    }

    if (isOpenAtLogin() !== auto) {
      app.setLoginItemSettings({ openAtLogin: auto })
      return isOpenAtLogin() === auto
    } else {
      return true
    }
  },
  skipProxy(): Promise<void> {
    return session.defaultSession.setProxy({ mode: 'direct' })
  }
}

interface ShortcutOptions {
  escToCloseWindow?: boolean
  zoom?: boolean
}

export const optimizer = {
  watchWindowShortcuts(window: BrowserWindow, shortcutOptions?: ShortcutOptions): void {
    if (!window) return

    const { webContents } = window
    const { escToCloseWindow = false, zoom = false } = shortcutOptions || {}

    webContents.on('before-input-event', (event, input) => {
      if (input.type === 'keyDown') {
        if (!is.dev) {
          if (input.code === 'KeyR' && (input.control || input.meta)) {
            event.preventDefault()
          }
          if (
            input.code === 'KeyI' &&
            ((input.alt && input.meta) || (input.control && input.shift))
          ) {
            event.preventDefault()
          }
        }

        if (input.code === 'Escape' && escToCloseWindow) {
          window.close()
        }

        if (!zoom) {
          if (
            input.code === 'Equal' &&
            (input.control || input.meta) &&
            webContents.getZoomFactor() < 2.0
          ) {
            event.preventDefault()
          }
          if (
            input.code === 'Minus' &&
            (input.control || input.meta) &&
            webContents.getZoomFactor() > 0.5
          ) {
            event.preventDefault()
          }
          if (input.code === 'Digit0' && (input.control || input.meta)) {
            event.preventDefault()
          }
        }
      }
    })
  },

  registerFramelessWindowIpc(): void {
    // Not implemented - not used in this project
  }
}
