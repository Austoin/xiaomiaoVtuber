import type { RouteRecordRaw } from 'vue-router'

import { describe, expect, it } from 'vitest'
import { defineComponent } from 'vue'

import { applyRouteLayouts } from './router'

describe('applyRouteLayouts', () => {
  it('wraps page routes with explicit and default layouts while preserving nested routes', () => {
    const defaultLayout = defineComponent({ name: 'DefaultLayout' })
    const settingsLayout = defineComponent({ name: 'SettingsLayout' })
    const settingsPage = defineComponent({ name: 'SettingsPage' })
    const providerPage = defineComponent({ name: 'ProviderPage' })
    const routes: RouteRecordRaw[] = [
      {
        path: '/settings',
        name: 'settings',
        component: settingsPage,
        meta: { layout: 'settings' },
        children: [
          {
            path: 'providers',
            name: 'providers',
            component: providerPage,
          },
        ],
      },
    ]

    const result = applyRouteLayouts(routes, {
      layouts: {
        default: defaultLayout,
        settings: settingsLayout,
      },
    })

    expect(result[0].component).toBe(settingsLayout)
    expect(result[0].name).toBeUndefined()
    expect(result[0].children).toHaveLength(1)

    const settingsPageRoute = result[0].children?.[0]
    expect(settingsPageRoute).toMatchObject({
      path: '',
      name: 'settings',
      component: settingsPage,
    })
    expect(settingsPageRoute?.children?.[0]).toMatchObject({
      path: 'providers',
      name: 'providers',
      component: providerPage,
    })
  })

  it('leaves top-level routes unwrapped when layouts are disabled', () => {
    const page = defineComponent({ name: 'StandalonePage' })
    const route: RouteRecordRaw = {
      path: '/standalone',
      name: 'standalone',
      component: page,
      meta: { layout: false },
    }

    const result = applyRouteLayouts([route], {
      layouts: {
        default: defineComponent({ name: 'DefaultLayout' }),
      },
    })

    expect(result).toEqual([route])
  })

  it('rejects unknown layout names instead of rendering an implicit fallback', () => {
    const page = defineComponent({ name: 'Page' })

    expect(() => applyRouteLayouts([
      {
        path: '/invalid',
        component: page,
        meta: { layout: 'missing' },
      },
    ], {
      layouts: {
        default: defineComponent({ name: 'DefaultLayout' }),
      },
    })).toThrowError('Unknown route layout "missing" for path "/invalid"')
  })
})
