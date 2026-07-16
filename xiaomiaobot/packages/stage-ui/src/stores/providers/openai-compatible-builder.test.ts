import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ProviderValidationCheck } from '../../libs/providers'
import { buildOpenAICompatibleProvider } from './openai-compatible-builder'

const { listModelsMock } = vi.hoisted(() => ({
  listModelsMock: vi.fn(),
}))

vi.mock('@xsai/model', () => ({
  listModels: listModelsMock,
}))

describe('buildOpenAICompatibleProvider', () => {
  let fetchMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    vi.clearAllMocks()
    listModelsMock.mockResolvedValue([{ id: 'test-model' }])
    fetchMock = vi.fn().mockResolvedValue(new Response('{}', { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('checks provider health without invoking a client-side model', async () => {
    const provider = buildOpenAICompatibleProvider({
      id: 'test',
      name: 'Test',
      icon: 'test',
      description: 'Test provider',
      nameKey: 'test.name',
      descriptionKey: 'test.description',
      creator: vi.fn(),
      validation: [ProviderValidationCheck.Health],
    })

    const result = await provider.validators.validateProviderConfig({
      apiKey: 'test-key',
      baseUrl: 'https://example.com/v1',
    })

    expect(result.valid).toBe(true)
    expect(fetchMock).toHaveBeenCalledWith(
      'https://example.com/v1/models',
      expect.objectContaining({ method: 'GET' }),
    )
  })
})
