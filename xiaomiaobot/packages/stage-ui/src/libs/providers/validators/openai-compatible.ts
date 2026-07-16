import type { ProviderDefinition, ProviderExtraMethods, ProviderInstance } from '../types'

import { errorMessageFrom } from '@moeru/std'
import { listModels } from '@xsai/model'

import { isModelProvider, ProviderValidationCheck } from '../types'

interface OpenAICompatibleValidationOptions<TConfig extends { apiKey?: string, baseUrl?: string }> {
  checks?: ProviderValidationCheck[]
  additionalHeaders?: Record<string, string>
  schedule?: {
    mode: 'once' | 'interval'
    intervalMs?: number
  }
  skipApiKeyCheck?: boolean
  connectivityFailureReason?: (input: { config: TConfig, error: unknown, errorMessage: string }) => string
  modelListFailureReason?: (input: { config: TConfig, error: unknown, errorMessage: string }) => string
}

async function resolveModels<TConfig extends { apiKey?: string | null, baseUrl?: string | URL | null }>(
  config: TConfig,
  provider: ProviderInstance,
  providerExtra: ProviderExtraMethods<TConfig> | undefined,
) {
  if (providerExtra?.listModels) {
    return providerExtra.listModels(config, provider)
  }
  if (!isModelProvider(provider)) {
    return listModels({ baseURL: config.baseUrl!, apiKey: config.apiKey! })
  }

  return listModels(provider.model())
}

export function createOpenAICompatibleValidators<TConfig extends { apiKey?: string, baseUrl?: string }>(
  options?: OpenAICompatibleValidationOptions<TConfig>,
): ProviderDefinition<TConfig>['validators'] {
  const checks = options?.checks ?? [ProviderValidationCheck.Connectivity, ProviderValidationCheck.ModelList]
  const additionalHeaders = options?.additionalHeaders
  const validatorConfig: ProviderDefinition<TConfig>['validators'] = {
    validateConfig: [],
    validateProvider: [],
  }

  validatorConfig.validateConfig?.push(({ t }) => ({
    id: 'openai-compatible:check-config',
    name: t('settings.pages.providers.catalog.edit.validators.openai-compatible.check-config.title'),
    validator: async (config) => {
      const errors: Array<{ error: unknown }> = []
      const apiKey = typeof config.apiKey === 'string' ? config.apiKey.trim() : ''
      const baseUrl = (config.baseUrl as string | URL | undefined) instanceof URL ? config.baseUrl?.toString() : (typeof config.baseUrl === 'string' ? config.baseUrl.trim() : '')

      if (!options?.skipApiKeyCheck && !apiKey)
        errors.push({ error: new Error('API key is required.') })
      if (!baseUrl)
        errors.push({ error: new Error('Base URL is required.') })

      if (baseUrl) {
        try {
          const parsed = new URL(baseUrl)
          if (!parsed.host)
            errors.push({ error: new Error('Base URL is not absolute. Check your input.') })
        }
        catch {
          errors.push({ error: new Error('Base URL is invalid. It must be an absolute URL.') })
        }
      }

      return {
        errors,
        reason: errors.length > 0 ? errors.map(item => (item.error as Error).message).join(', ') : '',
        reasonKey: '',
        valid: errors.length === 0,
      }
    },
  }))

  if (checks.includes(ProviderValidationCheck.Connectivity)) {
    validatorConfig.validateProvider?.push(({ t }) => ({
      id: 'openai-compatible:check-connectivity',
      name: t('settings.pages.providers.catalog.edit.validators.openai-compatible.check-connectivity.title'),
      schedule: options?.schedule,
      validator: async (config) => {
        const errors: Array<{ error: unknown }> = []
        const baseUrl = String(config.baseUrl ?? '')
        const modelsUrl = baseUrl.endsWith('/') ? `${baseUrl}models` : `${baseUrl}/models`
        const controller = new AbortController()
        const timeout = setTimeout(() => controller.abort(), 10_000)

        try {
          const response = await fetch(modelsUrl, {
            method: 'GET',
            headers: {
              ...(config.apiKey ? { Authorization: `Bearer ${config.apiKey}` } : {}),
              ...additionalHeaders,
            },
            signal: controller.signal,
          })

          if (response.status >= 500) {
            const errorMessage = `Server error: HTTP ${response.status}`
            const reason = options?.connectivityFailureReason
              ? options.connectivityFailureReason({ config, error: new Error(errorMessage), errorMessage })
              : `Connectivity check failed: ${errorMessage}`
            errors.push({ error: new Error(reason) })
          }
        }
        catch (e) {
          const errorMessage = errorMessageFrom(e) || 'Unknown error.'
          const reason = options?.connectivityFailureReason
            ? options.connectivityFailureReason({ config, error: e, errorMessage })
            : `Connectivity check failed: ${errorMessage}`
          errors.push({ error: new Error(reason) })
        }
        finally {
          clearTimeout(timeout)
        }

        return {
          errors,
          reason: errors.length > 0 ? errors.map(item => (item.error as Error).message).join(', ') : '',
          reasonKey: '',
          valid: errors.length === 0,
        }
      },
    }))
  }

  if (checks.includes(ProviderValidationCheck.ModelList)) {
    validatorConfig.validateProvider?.push(({ t }) => ({
      id: 'openai-compatible:check-model-list',
      name: t('settings.pages.providers.catalog.edit.validators.openai-compatible.check-supports-model-listing.title'),
      schedule: options?.schedule,
      validator: async (config, provider, providerExtra) => {
        const errors: Array<{ error: unknown }> = []
        try {
          const models = await resolveModels(config, provider, providerExtra)
          if (!models || models.length === 0) {
            errors.push({ error: new Error('Model list check failed: no models found') })
          }
        }
        catch (e) {
          const errorMessage = errorMessageFrom(e) || 'Unknown error.'
          const reason = options?.modelListFailureReason
            ? options.modelListFailureReason({ config, error: e, errorMessage })
            : `Model list check failed: ${errorMessage}`
          errors.push({ error: new Error(reason) })
        }

        return {
          errors,
          reason: errors.length > 0 ? errors.map(item => (item.error as Error).message).join(', ') : '',
          reasonKey: '',
          valid: errors.length === 0,
        }
      },
    }))
  }

  return validatorConfig
}
