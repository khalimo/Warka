'use client'

import { useLanguage } from './LanguageProvider'

export function SkipToContentLink() {
  const { dictionary } = useLanguage()

  return (
    <a href="#main-content" className="skip-link">
      {dictionary.accessibility.skipToContent}
    </a>
  )
}
