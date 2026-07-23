import type { Component } from 'vue'
import type { RouteRecordRaw } from 'vue-router'

import { defineAsyncComponent } from 'vue'

const DefaultLayout = defineAsyncComponent(() => import('./layouts/default.vue'))
const HomeLayout = defineAsyncComponent(() => import('./layouts/home.vue'))
const PlainLayout = defineAsyncComponent(() => import('./layouts/plain.vue'))
const SettingsLayout = defineAsyncComponent(() => import('./layouts/settings.vue'))
const StageLayout = defineAsyncComponent(() => import('./layouts/stage.vue'))

/** Options used to resolve route metadata into layout components. */
export interface StageLayoutOptions {
  /** Layout components indexed by the `layout` route metadata value. */
  layouts: Readonly<Record<string, Component>>
  /** Layout used when a route does not provide a `layout` metadata value. @default 'default' */
  defaultLayout?: string
}

const STAGE_LAYOUTS = {
  default: DefaultLayout,
  home: HomeLayout,
  plain: PlainLayout,
  settings: SettingsLayout,
  stage: StageLayout,
} satisfies Readonly<Record<string, Component>>

/**
 * Applies layout route records without a virtual Vite module.
 *
 * Use when:
 * - Auto-generated Vue Router routes carry `meta.layout` values.
 * - Layout components should remain regular route components.
 *
 * Expects:
 * - Every route layout name to exist in `options.layouts`.
 *
 * Returns:
 * - Route records whose page component is nested below its layout component.
 * - An error when a route names an unknown layout.
 */
export function applyRouteLayouts(routes: readonly RouteRecordRaw[], options: StageLayoutOptions): RouteRecordRaw[] {
  return routes.map(route => applyRouteLayout(route, options, true))
}

/**
 * Builds the application route records from the shared stage layouts.
 *
 * Use when:
 * - Creating a stage application router from `vue-router/auto-routes`.
 *
 * Expects:
 * - Route metadata may contain `layout: string`.
 *
 * Returns:
 * - Layout-wrapped route records for the stage applications.
 */
export function setupStageLayouts(routes: readonly RouteRecordRaw[]): RouteRecordRaw[] {
  return applyRouteLayouts(routes, { layouts: STAGE_LAYOUTS })
}

function applyRouteLayout(route: RouteRecordRaw, options: StageLayoutOptions, isTopLevel: boolean): RouteRecordRaw {
  const nestedChildren = route.children?.length
    ? route.children.map(child => applyRouteLayout(child, options, false))
    : undefined
  const routeWithChildren = nestedChildren ? { ...route, children: nestedChildren } : route

  if (!isTopLevel) {
    if (typeof route.meta?.layout !== 'string') {
      return routeWithChildren
    }

    return wrapRouteWithLayout(routeWithChildren, resolveLayout(route.meta.layout, route.path, options))
  }

  const hasNestedLayout = nestedChildren?.some(child => child.meta?.isLayout && (child.path === '' || child.path === '/'))
  if (route.meta?.layout === false || (!hasRouteComponent(route) && hasNestedLayout)) {
    return routeWithChildren
  }

  const layoutName = typeof route.meta?.layout === 'string'
    ? route.meta.layout
    : options.defaultLayout ?? 'default'

  return wrapRouteWithLayout(routeWithChildren, resolveLayout(layoutName, route.path, options))
}

function resolveLayout(layoutName: string, path: string, options: StageLayoutOptions): Component {
  const layout = options.layouts[layoutName]
  if (!layout) {
    throw new Error(`Unknown route layout "${layoutName}" for path "${path}"`)
  }

  return layout
}

function wrapRouteWithLayout(route: RouteRecordRaw, layout: Component): RouteRecordRaw {
  return {
    path: route.path,
    component: layout,
    children: [route.path === '/' ? route : { ...route, path: '' }],
    meta: { isLayout: true },
  }
}

function hasRouteComponent(route: RouteRecordRaw): boolean {
  return 'component' in route && !!route.component
}
