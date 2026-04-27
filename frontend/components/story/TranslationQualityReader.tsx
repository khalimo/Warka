'use client'

import { useState } from 'react'
import clsx from 'clsx'
import { ExternalLink, Languages } from 'lucide-react'
import { useLanguage } from '@/components/language/LanguageProvider'
import { AppLanguage, getDictionary } from '@/lib/i18n'
import { Story } from '@/lib/types'

type ReaderPane = 'original' | 'translated'
type Dictionary = ReturnType<typeof getDictionary>

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function textToHtml(value?: string) {
  const cleaned = value?.trim()
  return cleaned ? `<p>${escapeHtml(cleaned)}</p>` : ''
}

function languageName(lang: AppLanguage, dictionary: Dictionary) {
  return lang === 'so' ? dictionary.languages.so : dictionary.languages.en
}

function translationLanguages(story: Story): AppLanguage[] {
  const languages = new Set<AppLanguage>()
  const buckets = [
    story.translations?.content,
    story.translations?.summary,
    story.translations?.excerpt,
    story.translations?.headline,
  ]

  buckets.forEach((bucket) => {
    Object.keys(bucket || {}).forEach((key) => {
      if ((key === 'so' || key === 'en') && key !== story.lang) {
        languages.add(key)
      }
    })
  })

  return Array.from(languages)
}

function preferredTranslationLanguage(story: Story, lang: AppLanguage) {
  const available = translationLanguages(story)

  if (lang !== story.lang && story.translations?.content?.[lang]) {
    return lang
  }

  return available.find((availableLang) => story.translations?.content?.[availableLang])
}

function qualityNote(translationAvailable: boolean, dictionary: Dictionary) {
  if (!translationAvailable) {
    return dictionary.translation.reader.unavailableNote
  }

  return dictionary.translation.reader.machineNote
}

function ArticleBody({ html, emptyText }: { html: string; emptyText: string }) {
  if (!html) {
    return (
      <p className="text-base leading-7 text-ink/62 dark:text-[#cfc8be]">
        {emptyText}
      </p>
    )
  }

  return (
    <div
      className="prose prose-base max-w-none prose-headings:font-serif prose-headings:text-ink prose-p:text-[1rem] prose-p:leading-7 prose-p:text-ink/78 prose-a:text-primary-700 prose-strong:text-ink prose-li:text-ink/78 dark:prose-headings:text-[#fbf7f0] dark:prose-p:text-[#ddd7ce] dark:prose-a:text-primary-200 dark:prose-strong:text-[#fbf7f0] dark:prose-li:text-[#ddd7ce] sm:prose-lg sm:prose-p:text-[1.04rem] sm:prose-p:leading-8"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}

function ReaderColumn({
  eyebrow,
  title,
  helper,
  html,
}: {
  eyebrow: string
  title: string
  helper: string
  html: string
}) {
  return (
    <section className="rounded-editorial border border-[#d8cab7] bg-white/86 p-5 shadow-lift dark:border-white/10 dark:bg-[#182124] sm:p-6">
      <div className="mb-5 border-b news-divider pb-4">
        <p className="text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-primary-700 dark:text-primary-200">
          {eyebrow}
        </p>
        <h2 className="mt-2 text-xl font-semibold text-ink dark:text-[#fbf7f0]">{title}</h2>
        <p className="mt-2 text-sm leading-6 text-ink/62 dark:text-[#cfc8be]">{helper}</p>
      </div>
      <ArticleBody html={html} emptyText={helper} />
    </section>
  )
}

export function TranslationQualityReader({ story }: { story: Story }) {
  const { lang, dictionary } = useLanguage()
  const [activePane, setActivePane] = useState<ReaderPane>('original')
  const targetLang = preferredTranslationLanguage(story, lang)
  const originalHtml = story.content || textToHtml(story.summary || story.excerpt)
  const translatedHtml = targetLang ? story.translations?.content?.[targetLang] || '' : ''
  const translationAvailable = Boolean(translatedHtml)
  const originalLanguage = languageName(story.lang, dictionary)
  const translatedLanguage = targetLang ? languageName(targetLang, dictionary) : dictionary.translation.reader.notAvailable

  const panes: Array<{
    id: ReaderPane
    label: string
    eyebrow: string
    title: string
    helper: string
    html: string
  }> = [
    {
      id: 'original',
      label: dictionary.translation.reader.originalTab,
      eyebrow: dictionary.translation.reader.originalEyebrow,
      title: `${dictionary.translation.reader.originalText}: ${originalLanguage}`,
      helper: dictionary.translation.reader.originalNote,
      html: originalHtml,
    },
    {
      id: 'translated',
      label: dictionary.translation.reader.translatedTab,
      eyebrow: dictionary.translation.reader.translatedEyebrow,
      title: translationAvailable
        ? `${dictionary.translation.reader.translatedText}: ${translatedLanguage}`
        : dictionary.translation.reader.translationUnavailable,
      helper: qualityNote(translationAvailable, dictionary),
      html: translatedHtml,
    },
  ]
  const active = panes.find((pane) => pane.id === activePane) || panes[0]

  return (
    <section className="mb-10 sm:mb-12" aria-labelledby="translation-quality-title">
      <div className="mb-5 rounded-editorial border border-[#d8cab7] bg-white/82 p-5 dark:border-white/10 dark:bg-[#182124] sm:p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="flex items-center gap-2 text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-primary-700 dark:text-primary-200">
              <Languages className="h-4 w-4" aria-hidden="true" />
              {dictionary.translation.reader.kicker}
            </p>
            <h2 id="translation-quality-title" className="mt-2 text-2xl font-semibold text-ink dark:text-[#fbf7f0]">
              {dictionary.translation.reader.title}
            </h2>
            <p className="mt-2 max-w-[43rem] text-sm leading-6 text-ink/64 dark:text-[#cfc8be]">
              {dictionary.translation.reader.deck}
            </p>
          </div>
          <a
            href={story.originalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex min-h-[42px] shrink-0 items-center gap-2 rounded-full border border-primary-200 bg-primary-50 px-4 py-2 text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-primary-700 transition-colors duration-300 ease-editorial hover:bg-primary-100 dark:border-primary-900/60 dark:bg-primary-900/20 dark:text-primary-200 dark:hover:bg-primary-900/30"
          >
            {dictionary.translation.reader.sourceLink}
            <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
          </a>
        </div>

        <dl className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-editorial border border-[#ded2c0] bg-paper/70 px-4 py-3 dark:border-white/10 dark:bg-[#141d1f]">
            <dt className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#aaa39a]">
              {dictionary.translation.reader.originalLanguage}
            </dt>
            <dd className="mt-1 text-sm font-semibold text-ink/78 dark:text-[#eee7df]">{originalLanguage}</dd>
          </div>
          <div className="rounded-editorial border border-[#ded2c0] bg-paper/70 px-4 py-3 dark:border-white/10 dark:bg-[#141d1f]">
            <dt className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#aaa39a]">
              {dictionary.translation.reader.machineTranslated}
            </dt>
            <dd className="mt-1 text-sm font-semibold text-ink/78 dark:text-[#eee7df]">
              {translationAvailable ? translatedLanguage : dictionary.translation.reader.notAvailable}
            </dd>
          </div>
          <div className="rounded-editorial border border-[#ded2c0] bg-paper/70 px-4 py-3 dark:border-white/10 dark:bg-[#141d1f]">
            <dt className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#aaa39a]">
              {dictionary.translation.reader.confidence}
            </dt>
            <dd className="mt-1 text-sm font-semibold text-ink/78 dark:text-[#eee7df]">
              {dictionary.translation.reader.confidenceUnavailable}
            </dd>
          </div>
          <div className="rounded-editorial border border-[#ded2c0] bg-paper/70 px-4 py-3 dark:border-white/10 dark:bg-[#141d1f]">
            <dt className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#aaa39a]">
              {dictionary.translation.reader.reviewStatus}
            </dt>
            <dd className="mt-1 text-sm font-semibold text-ink/78 dark:text-[#eee7df]">
              {dictionary.translation.reader.notHumanReviewed}
            </dd>
          </div>
        </dl>
      </div>

      <div className="lg:hidden">
        <div className="mb-3 grid grid-cols-2 gap-2 rounded-editorial border border-[#d8cab7] bg-white/80 p-1.5 dark:border-white/10 dark:bg-[#182124]">
          {panes.map((pane) => (
            <button
              key={pane.id}
              type="button"
              onClick={() => setActivePane(pane.id)}
              className={clsx(
                'min-h-[42px] rounded-editorial px-3 py-2 text-sm font-semibold transition-colors duration-300 ease-editorial',
                activePane === pane.id
                  ? 'bg-primary-700 text-white shadow-sm dark:bg-primary-300 dark:text-[#12191b]'
                  : 'text-ink/62 hover:bg-paper dark:text-[#d6d0c7] dark:hover:bg-[#141d1f]'
              )}
            >
              {pane.label}
            </button>
          ))}
        </div>
        <ReaderColumn eyebrow={active.eyebrow} title={active.title} helper={active.helper} html={active.html} />
      </div>

      <div className={clsx('hidden gap-5 lg:grid', translationAvailable ? 'lg:grid-cols-2' : 'lg:grid-cols-1')}>
        <ReaderColumn eyebrow={panes[0].eyebrow} title={panes[0].title} helper={panes[0].helper} html={panes[0].html} />
        {translationAvailable ? (
          <ReaderColumn eyebrow={panes[1].eyebrow} title={panes[1].title} helper={panes[1].helper} html={panes[1].html} />
        ) : (
          <div className="rounded-editorial border border-acacia/25 bg-acacia/10 p-5 text-sm leading-6 text-ink/70 dark:border-acacia/20 dark:bg-acacia/10 dark:text-[#ddd7ce]">
            <p className="font-semibold text-acacia">{dictionary.translation.reader.translationUnavailable}</p>
            <p className="mt-2">{dictionary.translation.reader.unavailableNote}</p>
          </div>
        )}
      </div>
    </section>
  )
}
