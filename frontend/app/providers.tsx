'use client'

import { LanguageProvider } from '@/components/language/LanguageProvider'
import { SkipToContentLink } from '@/components/language/SkipToContentLink'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary>
      <LanguageProvider>
        <SkipToContentLink />
        {children}
      </LanguageProvider>
    </ErrorBoundary>
  )
}
