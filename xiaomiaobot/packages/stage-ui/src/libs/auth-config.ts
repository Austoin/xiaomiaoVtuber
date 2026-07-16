// Centralized OIDC client configuration for the web platform.
// Electron and Pocket have their own configs due to different client IDs and redirect strategies.

export const OIDC_CLIENT_ID = import.meta.env.VITE_OIDC_CLIENT_ID || 'airi-stage-web'
const runtimeOrigin = globalThis.location?.origin || 'http://127.0.0.1'
export const OIDC_REDIRECT_URI = `${runtimeOrigin}/auth/callback`
