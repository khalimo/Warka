'use client'

import Link from 'next/link'
import { ArrowLeft, ExternalLink } from 'lucide-react'
import { SourceBadge } from '@/components/story/SourceBadge'
import { StoryLanguageBadge } from '@/components/story/StoryLanguageBadge'
import { ClusterTrustMethodologyPanel } from '@/components/trust/TrustMethodologyPanel'
import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { TimeAgo } from '@/components/ui/TimeAgo'
import { useLanguage } from '@/components/language/LanguageProvider'
import { getCompareSourceStats } from '@/lib/intelligence'
import { getStoryExcerpt, getStoryHeadline } from '@/lib/storyPresentation'
import { CompareCluster, Story } from '@/lib/types'

function confidenceTone(confidence: number) {
  if (confidence >= 75) {
    return 'border-emerald-500/30 bg-emerald-50 text-emerald-800 dark:border-emerald-300/20 dark:bg-emerald-300/10 dark:text-emerald-100'
  }
  if (confidence >= 50) {
    return 'border-acacia/30 bg-acacia/10 text-acacia dark:border-acacia/20 dark:bg-acacia/10 dark:text-acacia'
  }
  return 'border-[#ded2c0] bg-white/70 text-ink/72 dark:border-white/10 dark:bg-[#141d1f] dark:text-[#d9d3ca]'
}

function sortStories(stories: Story[]) {
  return [...stories].sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime())
}

export function ClusterCoveragePageClient({ cluster }: { cluster: CompareCluster | null }) {
  const { lang, dictionary } = useLanguage()

  if (!cluster) {
    return (
      <div className="bg-paper dark:bg-[#141b1d]">
        <section className="container-custom py-16 md:py-20">
          <div className="mx-auto max-w-3xl">
            <EmptyState
              title={dictionary.coverageHub.notFoundTitle}
              message={dictionary.coverageHub.notFoundMessage}
            />
            <div className="mt-6 text-center">
              <Link
                href="/compare"
                className="inline-flex min-h-[44px] items-center justify-center rounded-full border border-primary-200 bg-primary-50 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.14em] text-primary-700 transition-colors hover:bg-primary-100 dark:border-primary-900/50 dark:bg-primary-900/20 dark:text-primary-200"
              >
                {dictionary.coverageHub.backToCompare}
              </Link>
            </div>
          </div>
        </section>
      </div>
    )
  }

  const stories = sortStories(cluster.stories)
  const summary = cluster.aiNeutralSummary || cluster.neutralSummary || cluster.commonFacts
  const differences = cluster.aiCoverageDifferences || cluster.coverageDifferences
  const sourceStats = getCompareSourceStats(cluster, dictionary)
  const confidence = cluster.confidenceScore ?? cluster.eventSignature?.confidence ?? 0

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <section className="border-b news-divider">
        <div className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
          <div className="mx-auto max-w-6xl">
            <Link
              href="/compare"
              className="mb-8 inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.14em] text-primary-600 transition-colors hover:text-primary-700 dark:text-primary-200 dark:hover:text-primary-100"
            >
              <ArrowLeft className="h-4 w-4" />
              {dictionary.coverageHub.backToCompare}
            </Link>

            <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-start">
              <div>
                <div className="mb-4 flex flex-wrap items-center gap-3">
                  <span className="signature-chip">{dictionary.coverageHub.kicker}</span>
                  <span className="text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-ink/45 dark:text-[#b7b1a8]">
                    {cluster.hasAISynthesis ? dictionary.coverageHub.aiAssisted : dictionary.coverageHub.deterministic}
                  </span>
                </div>
                <h1 className="max-w-[18ch] text-[2.4rem] font-bold leading-[0.96] text-ink dark:text-[#fbf7f0] sm:text-[3.4rem] lg:text-[4.2rem]">
                  {cluster.title}
                </h1>
                {summary ? (
                  <p className="mt-6 max-w-3xl text-base leading-8 text-ink/72 dark:text-[#d8d2ca] sm:text-lg">
                    {summary}
                  </p>
                ) : null}
              </div>

              <aside className="section-surface p-5">
                <div className="eyebrow">{dictionary.coverageHub.eventSnapshot}</div>
                <div className="mt-4 grid gap-3">
                  {sourceStats.map((item) => (
                    <div key={item.label} className="rounded-editorial border border-[#ded2c0] bg-paper/70 px-4 py-3 dark:border-white/10 dark:bg-[#141d1f]">
                      <div className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/48 dark:text-[#b7b1a8]">
                        {item.label}
                      </div>
                      <div className="mt-1 font-serif text-[1.45rem] font-bold leading-none text-ink dark:text-[#fbf7f0]">
                        {item.value}
                      </div>
                    </div>
                  ))}
                  <div className={`rounded-editorial border px-4 py-3 ${confidenceTone(confidence)}`}>
                    <div className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] opacity-70">
                      {dictionary.compare.clusterConfidence}
                    </div>
                    <div className="mt-1 font-serif text-[1.45rem] font-bold leading-none">
                      {confidence || dictionary.trustMethodology.confidenceNew}
                    </div>
                  </div>
                </div>
              </aside>
            </div>
          </div>
        </div>
      </section>

      <section className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
        <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-start">
          <div className="space-y-8">
            <ClusterTrustMethodologyPanel cluster={cluster} lang={lang} dictionary={dictionary} />

            <section className="grid gap-5 md:grid-cols-2">
              <div className="rounded-editorial border border-acacia/25 bg-acacia/10 p-5 dark:border-acacia/20 dark:bg-acacia/10">
                <h2 className="mb-3 text-sm font-semibold uppercase tracking-[0.14em] text-acacia">
                  {dictionary.compare.agreement}
                </h2>
                <p className="text-sm leading-7 text-ink/78 dark:text-[#e2ddd5]">
                  {cluster.commonFacts || cluster.neutralSummary || dictionary.coverageHub.noAgreement}
                </p>
              </div>
              <div className="rounded-editorial border border-[#d8cab7] bg-white/82 p-5 dark:border-white/10 dark:bg-[#182124]">
                <h2 className="mb-3 text-sm font-semibold uppercase tracking-[0.14em] text-ink/58 dark:text-[#bbb4ab]">
                  {dictionary.compare.differences}
                </h2>
                <p className="text-sm leading-7 text-ink/74 dark:text-[#d9d3ca]">
                  {differences || dictionary.coverageHub.noDifferences}
                </p>
              </div>
            </section>

            <section>
              <SectionHeader
                title={dictionary.coverageHub.timelineTitle}
                subtitle={dictionary.coverageHub.timelineSubtitle}
              />
              {stories.length > 0 ? (
                <div className="section-surface overflow-hidden">
                  <div className="divide-y divide-[#dfd4c3] dark:divide-white/10">
                    {stories.map((story, index) => (
                      <article key={story.id} className="grid gap-4 p-5 sm:grid-cols-[8rem_minmax(0,1fr)] sm:p-6">
                        <div className="text-sm font-semibold text-ink/56 dark:text-[#bdb6ad]">
                          <TimeAgo date={story.publishedAt} />
                          <div className="mt-2 h-full border-l border-[#dfd4c3] pl-3 text-xs uppercase tracking-[0.14em] text-ink/40 dark:border-white/10 dark:text-[#9d968d]">
                            {index === 0 ? dictionary.coverageHub.latestReport : dictionary.coverageHub.relatedReport}
                          </div>
                        </div>
                        <div>
                          <div className="mb-3 flex flex-wrap items-center gap-2">
                            <StoryLanguageBadge story={story} compact />
                            <SourceBadge source={story.source} size="sm" />
                          </div>
                          <h3 className="font-serif text-xl font-bold leading-tight text-ink dark:text-[#fbf7f0]">
                            <Link href={`/story/${story.slug}`} className="editorial-link hover:text-primary-700 dark:hover:text-primary-200">
                              {getStoryHeadline(story, lang)}
                            </Link>
                          </h3>
                          <p className="mt-2 text-sm leading-7 text-ink/70 dark:text-[#d8d2ca]">
                            {getStoryExcerpt(story, lang)}
                          </p>
                          <div className="mt-4 flex flex-wrap gap-3">
                            <Link
                              href={`/story/${story.slug}`}
                              className="inline-flex min-h-[40px] items-center rounded-full border border-[#d8cab7] bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-ink transition-colors hover:bg-paper dark:border-white/10 dark:bg-[#141d1f] dark:text-[#fbf7f0]"
                            >
                              {dictionary.coverageHub.readOnWarka}
                            </Link>
                            <Link
                              href={story.originalUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex min-h-[40px] items-center gap-2 rounded-full border border-primary-200 bg-primary-50 px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-primary-700 transition-colors hover:bg-primary-100 dark:border-primary-900/50 dark:bg-primary-900/20 dark:text-primary-200"
                            >
                              {dictionary.coverageHub.originalSource}
                              <ExternalLink className="h-3.5 w-3.5" />
                            </Link>
                          </div>
                        </div>
                      </article>
                    ))}
                  </div>
                </div>
              ) : (
                <EmptyState
                  title={dictionary.coverageHub.noStoriesTitle}
                  message={dictionary.coverageHub.noStoriesMessage}
                />
              )}
            </section>
          </div>

          <aside className="section-surface sticky top-28 p-5">
            <div className="eyebrow">{dictionary.coverageHub.sourcesTitle}</div>
            <div className="mt-4 space-y-3">
              {cluster.sources.length > 0 ? cluster.sources.map((source) => (
                <div key={source.id} className="rounded-editorial border border-[#ded2c0] bg-paper/70 p-3 dark:border-white/10 dark:bg-[#141d1f]">
                  <SourceBadge source={source} size="sm" />
                  <p className="mt-2 text-xs leading-5 text-ink/58 dark:text-[#bdb6ad]">
                    {source.description || source.category || dictionary.coverageHub.sourceFallback}
                  </p>
                </div>
              )) : (
                <p className="text-sm leading-6 text-ink/64 dark:text-[#cfc8bf]">{dictionary.coverageHub.noSources}</p>
              )}
            </div>
          </aside>
        </div>
      </section>
    </div>
  )
}
