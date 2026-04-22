'use client'

import { formatRelativeTime } from '@/lib/i18n'
import { useLanguage } from '@/components/language/LanguageProvider'

export function TimeAgo({ date }: { date: string }) {
  const { lang } = useLanguage()

  return <time dateTime={date}>{formatRelativeTime(date, lang)}</time>
}
