import type { ComposerTranslation } from 'vue-i18n'

import type { ProviderExtraMethods, ProviderInstance } from '../types'

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ProviderValidationCheck } from '../types'
import { createOpenAICompatibleValidators } from './openai-compatible'

const { listModelsMock } = vi.hoisted(() => ({
  listModelsMock: vi.fn(),
}))

vi.mock('@xsai/model', () => ({
  listModels: listModelsMock,
}))

const mockT = vi.fn((key: string) => key) as unknown as ComposerTranslation

function getProviderValidators(options?: Parameters<typeof createOpenAICompatibleValidators>[0]) {
  const validators = createOpenAICompatibleValidators(options)

  return (validators?.validateProvider || []).map(create => create({ t: mockT }))
}

interface TestConfig { apiKey?: string, baseUrl?: string }

describe('createOpenAICompatibleValidators', () => {
  const config: TestConfig = {
    apiKey: 'test-key',
    baseUrl: 'https://example.com/v1/',
  }
  const provider: ProviderInstance = {
    model: () => ({
      apiKey: config.apiKey,
      baseURL: config.baseUrl,
    }),
  } as ProviderInstance
  const providerExtra: ProviderExtraMethods<TestConfig> = {}

  let fetchMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    vi.clearAllMocks()
    fetchMock = vi.fn().mockResolvedValue(new Response('{}', { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('connectivity check uses lightweight fetch', async () => {
    const [connectivityValidator] = getProviderValidators({
      checks: [ProviderValidationCheck.Connectivity],
    })

    const result = await connectivityValidator.validator(config, provider, providerExtra, { t: mockT })

    expect(result.valid).toBe(true)
    expect(fetchMock).toHaveBeenCalledWith(
      'https://example.com/v1/models',
      expect.objectContaining({ method: 'GET' }),
    )
  })

  it('connectivity check fails on network error', async () => {
    fetchMock.mockRejectedValue(new TypeError('fetch failed'))

    const [connectivityValidator] = getProviderValidators({
      checks: [ProviderValidationCheck.Connectivity],
    })

    const result = await connectivityValidator.validator(config, provider, providerExtra, { t: mockT })

    expect(result.valid).toBe(false)
    expect(result.reason).toContain('Connectivity check failed')
  })

  it('default checks do not include chat_completions', () => {
    const validators = getProviderValidators()
    const ids = validators.map(v => v.id)

    expect(ids).toContain('openai-compatible:check-connectivity')
    expect(ids).toContain('openai-compatible:check-model-list')
    expect(ids).not.toContain('openai-compatible:check-chat-completions')
  })

  it('does not register client-side chat completion probes', () => {
    const validators = getProviderValidators({
      checks: [ProviderValidationCheck.ChatCompletions],
    })

    expect(validators).toHaveLength(0)
  })
})
