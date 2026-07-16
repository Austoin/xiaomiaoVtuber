import messages from '@proj-airi/i18n/locales'

import { resolveSupportedLocale } from '@proj-airi/i18n'
import { createI18n } from 'vue-i18n'

function getLocale() {
  let language: string | null = null
  try {
    language = globalThis.localStorage?.getItem('settings/language') ?? null
  }
  catch {
    language = null
  }

  if (!language)
    language = globalThis.navigator?.language || 'en'

  return resolveSupportedLocale(language, Object.keys(messages!))
}

export const i18n = createI18n({
  legacy: false,
  locale: getLocale(),
  fallbackLocale: 'en',
  messages,
})
