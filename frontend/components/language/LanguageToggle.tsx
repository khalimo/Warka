'use client'

import clsx from 'clsx'
import { languages } from '@/lib/i18n'
import { useLanguage } from './LanguageProvider'

export function LanguageToggle({ compact = false }: { compact?: boolean }) {
  const { lang, setLang, dictionary } = useLanguage()

  const options = [
    {
      value: languages.SO,
      label: dictionary.languages.so,
      ariaLabel: dictionary.accessibility.switchToSomali,
    },
    {
      value: languages.EN,
      label: dictionary.languages.en,
      ariaLabel: dictionary.accessibility.switchToEnglish,
    },
  ]

  return (
    <div
      className={clsx(
        'inline-flex items-center rounded-full border border-[#d9ccb9] bg-white/90 p-1 shadow-sm dark:border-white/10 dark:bg-[#182124]',
        compact ? 'gap-1' : 'gap-1.5'
      )}
      role="group"
      aria-label={dictionary.cards.languageLabel}
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => setLang(option.value)}
          aria-pressed={lang === option.value}
          aria-label={option.ariaLabel}
          className={clsx(
            'rounded-full px-3 py-2 text-sm font-semibold transition-colors duration-300 ease-editorial',
            compact ? 'min-h-[40px]' : 'min-h-[44px]',
            lang === option.value
              ? 'bg-ink text-white dark:bg-[#f4efe7] dark:text-[#142024]'
              : 'text-ink/70 hover:text-ink dark:text-[#e1dbd2] dark:hover:text-white'
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}
