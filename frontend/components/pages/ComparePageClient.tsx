'use client'

import Link from 'next/link'
import { CompareClusterCard } from '@/components/compare/CompareClusterCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { useLanguage } from '@/components/language/LanguageProvider'
import { CompareCluster } from '@/lib/types'

type ActiveLensFilters = {
  language: string
  sourceCategory: string
  confidence: string
  recent: string
  sources: string
}

export function ComparePageClient({
  clusters,
  total = clusters.length,
  limit = 20,
  offset = 0,
  activeSourceCount = 0,
  readyStoryCount = 0,
  apiUnavailable = false,
  activeFilter = 'all',
  activeLensFilters = {
    language: 'all',
    sourceCategory: 'all',
    confidence: 'all',
    recent: 'all',
    sources: 'all',
  },
}: {
  clusters: CompareCluster[]
  total?: number
  limit?: number
  offset?: number
  activeSourceCount?: number
  readyStoryCount?: number
  apiUnavailable?: boolean
  activeFilter?: string
  activeLensFilters?: ActiveLensFilters
}) {
  const { dictionary } = useLanguage()
  const currentPage = Math.floor(offset / limit) + 1
  const hasPrevious = offset > 0
  const hasMore = offset + clusters.length < total
  const comparisonLabel = `${total.toLocaleString()} coverage ${total === 1 ? 'comparison' : 'comparisons'}`
  const filterItems = ['all', 'somalia', 'world', 'politics', 'security', 'humanitarian', 'economy']
  const filterLabel = activeFilter === 'all' ? 'all coverage' : activeFilter
  const activeLensCount = Object.values(activeLensFilters).filter((value) => value !== 'all').length

  const emptyTitle = apiUnavailable
    ? 'Warka is waking up'
    : readyStoryCount > 0
      ? 'Coverage comparisons are being prepared'
      : dictionary.compare.watchTitle
  const emptyMessage = apiUnavailable
    ? 'The API did not respond just now. Free-tier hosting can take a moment to wake, so please try again shortly.'
    : readyStoryCount > 0
      ? activeFilter === 'all'
        ? 'Stories have been collected, but Warka needs at least two related reports before comparison cards appear.'
        : `Stories exist, but no renderable ${filterLabel} comparison matched the active source lens filters yet.`
      : dictionary.compare.watchMessage

  function buildCompareHref(
    next: Partial<ActiveLensFilters & { filter: string; page: string }> = {}
  ) {
    const params = new URLSearchParams()
    const nextFilter = next.filter ?? activeFilter
    const language = next.language ?? activeLensFilters.language
    const sourceCategory = next.sourceCategory ?? activeLensFilters.sourceCategory
    const confidence = next.confidence ?? activeLensFilters.confidence
    const recent = next.recent ?? activeLensFilters.recent
    const sources = next.sources ?? activeLensFilters.sources

    if (nextFilter !== 'all') params.set('filter', nextFilter)
    if (language !== 'all') params.set('language', language)
    if (sourceCategory !== 'all') params.set('source_category', sourceCategory)
    if (confidence !== 'all') params.set('confidence', confidence)
    if (recent !== 'all') params.set('recent', recent)
    if (sources !== 'all') params.set('sources', sources)
    if (next.page) params.set('page', next.page)

    const query = params.toString()
    return query ? `/compare?${query}` : '/compare'
  }

  const FilterControls = (
    <div className="mt-6 space-y-5 rounded-editorial border border-[#ded2c0] bg-white/70 p-4 dark:border-white/10 dark:bg-[#182124]">
      <div>
        <div className="mb-3 text-center text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-ink/48 dark:text-[#b7b1a8]">
          {dictionary.sourceLens.coverageTopic}
        </div>
        <div className="flex flex-wrap justify-center gap-2">
          {filterItems.map((item) => {
            const isActive = item === activeFilter
            return (
              <Link
                key={item}
                href={buildCompareHref({ filter: item })}
                className={`rounded-full border px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.12em] transition-colors ${
                  isActive
                    ? 'border-primary-300 bg-primary-100 text-primary-800 dark:border-primary-700 dark:bg-primary-900/30 dark:text-primary-100'
                    : 'border-[#ded2c0] bg-white/70 text-ink/60 hover:bg-paper dark:border-white/10 dark:bg-[#141d1f] dark:text-[#d7d2ca]'
                }`}
              >
                {item === 'all' ? dictionary.sourceLens.all : item}
              </Link>
            )
          })}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {[
          {
            key: 'language',
            label: dictionary.sourceLens.language,
            active: activeLensFilters.language,
            options: [
              ['all', dictionary.sourceLens.all],
              ['so', dictionary.languages.so],
              ['en', dictionary.languages.en],
            ],
          },
          {
            key: 'sourceCategory',
            label: dictionary.sourceLens.sourceCategory,
            active: activeLensFilters.sourceCategory,
            options: [
              ['all', dictionary.sourceLens.all],
              ['news', dictionary.sourceLens.news],
              ['international', dictionary.sourceLens.international],
              ['humanitarian', dictionary.sourceLens.humanitarian],
              ['diaspora', dictionary.sourceLens.diaspora],
            ],
          },
          {
            key: 'confidence',
            label: dictionary.sourceLens.confidence,
            active: activeLensFilters.confidence,
            options: [
              ['all', dictionary.sourceLens.all],
              ['high', dictionary.sourceLens.high],
              ['medium', dictionary.sourceLens.medium],
              ['low', dictionary.sourceLens.low],
            ],
          },
          {
            key: 'recent',
            label: dictionary.sourceLens.recency,
            active: activeLensFilters.recent,
            options: [
              ['all', dictionary.sourceLens.anyTime],
              ['24', dictionary.sourceLens.day],
              ['72', dictionary.sourceLens.threeDays],
              ['168', dictionary.sourceLens.week],
            ],
          },
          {
            key: 'sources',
            label: dictionary.sourceLens.sourceCount,
            active: activeLensFilters.sources,
            options: [
              ['all', dictionary.sourceLens.anySources],
              ['2plus', dictionary.sourceLens.twoPlus],
              ['3plus', dictionary.sourceLens.threePlus],
              ['4plus', dictionary.sourceLens.fourPlus],
            ],
          },
        ].map((group) => (
          <div key={group.key}>
            <div className="mb-2 text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#aaa39a]">
              {group.label}
            </div>
            <div className="flex flex-wrap gap-2">
              {group.options.map(([value, label]) => {
                const isActive = value === group.active
                return (
                  <Link
                    key={value}
                    href={buildCompareHref({ [group.key]: value } as Partial<ActiveLensFilters>)}
                    className={`rounded-full border px-2.5 py-1 text-xs font-semibold transition-colors ${
                      isActive
                        ? 'border-primary-300 bg-primary-100 text-primary-800 dark:border-primary-700 dark:bg-primary-900/30 dark:text-primary-100'
                        : 'border-[#ded2c0] bg-paper/70 text-ink/62 hover:bg-white dark:border-white/10 dark:bg-[#141d1f] dark:text-[#d7d2ca]'
                    }`}
                  >
                    {label}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </div>
      {activeLensCount > 0 || activeFilter !== 'all' ? (
        <div className="flex justify-center border-t news-divider pt-4">
          <Link
            href="/compare"
            className="text-xs font-semibold uppercase tracking-[0.14em] text-primary-600 hover:text-primary-700 dark:text-primary-200"
          >
            {dictionary.sourceLens.clearFilters}
          </Link>
        </div>
      ) : null}
    </div>
  )

  if (clusters.length === 0) {
    return (
      <div className="bg-paper dark:bg-[#141b1d]">
        <section className="container-custom py-16 md:py-20">
          <div className="mx-auto max-w-4xl">
            <div className="mb-8">
              <EmptyState
                title={emptyTitle}
                message={emptyMessage}
              />
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                ['Available comparisons', total],
                [dictionary.compare.activeSources, activeSourceCount],
                [dictionary.compare.scannedStories, readyStoryCount],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-editorial border border-[#ded2c0] bg-white/80 px-4 py-4 text-center dark:border-white/10 dark:bg-[#182124]"
                >
                  <div className="font-serif text-3xl font-bold text-ink dark:text-[#fbf7f0]">{value}</div>
                  <div className="mt-1 text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-ink/48 dark:text-[#b7b1a8]">
                    {label}
                  </div>
                </div>
              ))}
            </div>
            {FilterControls}
          </div>
        </section>
      </div>
    )
  }

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <section className="border-b news-divider">
        <div className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
          <div className="mx-auto max-w-5xl">
            <div className="mb-5 flex justify-center sm:mb-6">
              <span className="signature-chip">{dictionary.sections.compareCoverage}</span>
            </div>
            <SectionHeader
              title={dictionary.pages.compare.title}
              subtitle={`${comparisonLabel} in ${filterLabel}. ${dictionary.pages.compare.subtitle}`}
              centered
            />
            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              {[
                ['Available comparisons', total],
                [dictionary.compare.activeSources, activeSourceCount],
                [dictionary.compare.scannedStories, readyStoryCount],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-editorial border border-[#ded2c0] bg-white/80 px-4 py-4 text-center dark:border-white/10 dark:bg-[#182124]"
                >
                  <div className="font-serif text-3xl font-bold text-ink dark:text-[#fbf7f0]">{value}</div>
                  <div className="mt-1 text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-ink/48 dark:text-[#b7b1a8]">
                    {label}
                  </div>
                </div>
              ))}
            </div>
            {FilterControls}
          </div>
        </div>
      </section>

      <section className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
        <div className="mx-auto max-w-5xl space-y-6 sm:space-y-8 md:space-y-10">
          {clusters.map((cluster) => (
            <CompareClusterCard key={cluster.id} cluster={cluster} />
          ))}
          {(hasPrevious || hasMore) ? (
            <div className="flex flex-col gap-3 border-t news-divider pt-6 sm:flex-row sm:items-center sm:justify-between">
              <div className="text-sm font-medium text-ink/60 dark:text-[#cfc8bf]">
                Page {currentPage} - showing {clusters.length} of {total.toLocaleString()}
              </div>
              <div className="flex gap-3">
                {hasPrevious ? (
                  <Link
                    href={buildCompareHref({ page: String(currentPage - 1) })}
                    className="inline-flex min-h-[44px] items-center justify-center rounded-full border border-[#d8cab7] bg-white px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.14em] text-ink transition-colors hover:bg-paper dark:border-white/10 dark:bg-[#182124] dark:text-[#fbf7f0]"
                  >
                    Previous
                  </Link>
                ) : null}
                {hasMore ? (
                  <Link
                    href={buildCompareHref({ page: String(currentPage + 1) })}
                    className="inline-flex min-h-[44px] items-center justify-center rounded-full border border-primary-200 bg-primary-50 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.14em] text-primary-700 transition-colors hover:bg-primary-100 dark:border-primary-900/50 dark:bg-primary-900/20 dark:text-primary-200"
                  >
                    Load more
                  </Link>
                ) : null}
              </div>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  )
}
