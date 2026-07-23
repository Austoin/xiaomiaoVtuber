export * from './events'

/**
 * Shared websocket endpoint path for the AIRI server channel.
 *
 * Keeping this value in the protocol package prevents server, client, and QR
 * onboarding URLs from silently drifting apart.
 */
export const SERVER_CHANNEL_WEBSOCKET_PATH = '/ws' as const
