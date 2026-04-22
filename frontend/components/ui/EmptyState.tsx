'use client'

import { useLanguage } from '@/components/language/LanguageProvider'

interface EmptyStateProps {
  title?: string
  message?: string
}

export function EmptyState({
  title,
  message,
}: EmptyStateProps) {
  const { dictionary } = useLanguage()

  return (
    <div className="section-surface px-6 py-12 text-center md:px-10">
      <div className="eyebrow mb-3">{dictionary.brand.name}</div>
      <p className="font-serif text-2xl font-bold text-ink dark:text-[#fbf7f0]">
        {title || dictionary.states.genericEmptyTitle}
      </p>
      <p className="mx-auto mt-3 max-w-2xl text-sm leading-7 text-ink/62 dark:text-[#cbc5bc]">
        {message || dictionary.states.genericEmptyMessage}
      </p>
    </div>
  )
}
