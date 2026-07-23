import type { CapabilityDescriptor } from '@proj-airi/plugin-sdk'

import { defineInvokeEventa } from '@moeru/eventa'

/**
 * Plugin capability state change payload reported by renderer or plugin code.
 *
 * Use when:
 * - Updating one plugin capability lifecycle state through the host bridge
 *
 * Expects:
 * - `key` matches a capability known to the plugin host or plugin SDK
 *
 * Returns:
 * - N/A
 */
export type PluginCapabilityPayload = Omit<CapabilityDescriptor, 'updatedAt'>

/**
 * Plugin capability snapshot stored by the host.
 *
 * Use when:
 * - Inspecting plugin capability lifecycle state in renderer tooling
 *
 * Expects:
 * - `updatedAt` is a millisecond timestamp from the host process
 *
 * Returns:
 * - N/A
 */
export type PluginCapabilityState = CapabilityDescriptor

export const pluginProtocolListProvidersEventName = 'proj-airi:plugin-sdk:apis:protocol:resources:providers:list-providers'
export const pluginProtocolListProviders = defineInvokeEventa<Array<{ name: string }>>(pluginProtocolListProvidersEventName)
export const electronPluginUpdateCapability = defineInvokeEventa<PluginCapabilityState, PluginCapabilityPayload>('eventa:invoke:electron:plugins:capability:update')
