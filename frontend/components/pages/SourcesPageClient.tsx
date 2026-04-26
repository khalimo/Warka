'use client'

import { SourceBadge } from '@/components/story/SourceBadge'
import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { TimeAgo } from '@/components/ui/TimeAgo'
import { useLanguage } from '@/components/language/LanguageProvider'
import { Source } from '@/lib/types'

function uniqueCount(values: Array<string | undefined>) {
  return new Set(values.filter(Boolean)).size
}

function languageLabel(value?: string) {
  if (!value) return 'unknown'
  return value.toLowerCase().startsWith('so') ? 'Somali' : 'English'
}

function categoryLabel(value?: string) {
  return (value || 'general').replace(/_/g, ' ')
}

export function SourcesPageClient({ sources }: { sources: Source[] }) {
  const { dictionary } = useLanguage()

  if (sources.length === 0) {
    return (
      <div className="container-custom py-16 md:py-20">
        <EmptyState
          title={dictionary.pages.sources.emptyTitle}
          message={dictionary.pages.sources.emptyMessage}
        />
      </div>
    )
  }

  const categories = uniqueCount(sources.map((source) => source.category))
  const languages = uniqueCount(sources.map((source) => source.language))

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <section className="border-b news-divider">
        <div className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
          <div className="mx-auto max-w-5xl">
            <SectionHeader title={dictionary.pages.sources.title} subtitle={dictionary.pages.sources.subtitle} />
            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              {[
                [dictionary.pages.sources.activeSources, sources.length],
                [dictionary.pages.sources.languages, languages],
                [dictionary.pages.sources.categories, categories],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-editorial border border-[#ded2c0] bg-white/80 px-4 py-4 dark:border-white/10 dark:bg-[#182124]"
                >
                  <div className="font-serif text-3xl font-bold text-ink dark:text-[#fbf7f0]">{value}</div>
                  <div className="mt-1 text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-ink/48 dark:text-[#b7b1a8]">
                    {label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
        <div className="mx-auto grid max-w-6xl gap-4 md:grid-cols-2 xl:grid-cols-3">
          {sources.map((source) => (
            <article
              key={source.id}
              className="rounded-editorial border border-[#ded2c0] bg-white/88 p-5 shadow-sm dark:border-white/10 dark:bg-[#182124]"
            >
              <div className="mb-4">
                <SourceBadge source={source} />
              </div>
              <p className="min-h-[4.5rem] text-sm leading-6 text-ink/68 dark:text-[#d8d2ca]">
                {source.description || source.name}
              </p>
              <dl className="mt-5 space-y-3 border-t news-divider pt-4">
                <div>
                  <dt className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#a9a39a]">
                    {dictionary.cards.languageLabel}
                  </dt>
                  <dd className="mt-1 text-sm font-medium text-ink/78 dark:text-[#e0dbd2]">
                    {languageLabel(source.language)}
                  </dd>
                </div>
                <div>
                  <dt className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#a9a39a]">
                    {dictionary.cards.sourceLabel}
                  </dt>
                  <dd className="mt-1 text-sm font-medium capitalize text-ink/78 dark:text-[#e0dbd2]">
                    {categoryLabel(source.category)}
                  </dd>
                </div>
                <div>
                  <dt className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#a9a39a]">
                    {dictionary.pages.sources.lastUpdated}
                  </dt>
                  <dd className="mt-1 text-sm font-medium text-ink/78 dark:text-[#e0dbd2]">
                    {source.lastSuccessAt ? <TimeAgo date={source.lastSuccessAt} /> : dictionary.pages.sources.noUpdate}
                  </dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
