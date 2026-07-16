import { hc } from 'hono/client'

import { authedFetch } from '../libs/auth-fetch'
import { SERVER_URL } from '../libs/server'

// The optional cloud service is external to this local Agent workspace.

export const client = hc<any>(SERVER_URL, {
  fetch: authedFetch,

}) as any
