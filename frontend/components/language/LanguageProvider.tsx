'use client'

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { AppLanguage, defaultLang, getDictionary, getStoredLanguage, setStoredLanguage } from '@/lib/i18n'

interface LanguageContextValue {
  lang: AppLanguage
  setLang: (lang: AppLanguage) => void
  dictionary: ReturnType<typeof getDictionary>
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<AppLanguage>(defaultLang)

  const setLang = useCallback((nextLang: AppLanguage) => {
    setLangState(nextLang)
    setStoredLanguage(nextLang)
  }, [])

  useEffect(() => {
    setLangState(getStoredLanguage())
  }, [])

  useEffect(() => {
    const syncLanguage = () => setLangState(getStoredLanguage())
    window.addEventListener('languagechange', syncLanguage)
    window.addEventListener('storage', syncLanguage)

    return () => {
      window.removeEventListener('languagechange', syncLanguage)
      window.removeEventListener('storage', syncLanguage)
    }
  }, [])

  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  const value = useMemo(
    () => ({
      lang,
      setLang,
      dictionary: getDictionary(lang),
    }),
    [lang, setLang]
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage() {
  const context = useContext(LanguageContext)

  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider')
  }

  return context
}
