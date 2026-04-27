'use client'

import Link from 'next/link'
import { ArrowLeft, CalendarClock, ExternalLink } from 'lucide-react'
import { ShareLinkButton } from '@/components/share/ShareLinkButton'
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
  return [...stories].sort((a, b) => {
    const aTime = getStoryTime(a)
    const bTime = getStoryTime(b)

    if (aTime === null && bTime === null) {
      return a.title.localeCompare(b.title)
    }

    if (aTime === null) {
      return 1
    }

    if (bTime === null) {
      return -1
    }

    return aTime - bTime
  })
}

function getStoryTime(story: Story) {
  const time = new Date(story.publishedAt).getTime()
  return Number.isFinite(time) ? time : null
}

function getTimelineDate(story: Story) {
  const time = getStoryTime(story)
  return time === null ? null : new Date(time)
}

function formatTimelineDate(date: Date | null, lang: string) {
  if (!date) {
    return null
  }

  return new Intl.DateTimeFormat(lang, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(date)
}

function formatTimelineTime(date: Date | null, lang: string) {
  if (!date) {
    return null
  }

  return new Intl.DateTimeFormat(lang, {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function getDayKey(story: Story) {
  const date = getTimelineDate(story)
  return date ? date.toISOString().slice(0, 10) : 'unknown'
}

function groupStoriesByDay(stories: Story[]) {
  return stories.reduce<Array<{ key: string; date: Date | null; stories: Story[] }>>((groups, story) => {
    const key = getDayKey(story)
    const existing = groups.find((group) => group.key === key)

    if (existing) {
      existing.stories.push(story)
      return groups
    }

    groups.push({
      key,
      date: getTimelineDate(story),
      stories: [story],
    })
    return groups
  }, [])
}

function storyLanguageLabel(story: Story) {
  return (story.source.language || story.lang || '').toUpperCase() || '—'
}

function storyRegionLabel(story: Story) {
  return [story.region, story.category].filter(Boolean).join(' / ')
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
  const timelineGroups = groupStoriesByDay(stories)
  const firstStory = stories[0]
  const latestStory = stories[stories.length - 1]
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
                <div className="mt-6 flex flex-wrap gap-3">
                  <ShareLinkButton
                    path={`/compare/${encodeURIComponent(cluster.id)}`}
                    title={cluster.title}
                    summary={summary}
                  />
                  <Link
                    href={`/compare/${encodeURIComponent(cluster.id)}/opengraph-image`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex min-h-[40px] items-center justify-center rounded-full border border-[#d8cab7] bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-ink transition-colors hover:bg-paper dark:border-white/10 dark:bg-[#141d1f] dark:text-[#fbf7f0] sm:px-5"
                  >
                    {dictionary.share.previewCard}
                  </Link>
                </div>
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
                <div className="space-y-5">
                  <div className="grid gap-3 md:grid-cols-2">
                    {[firstStory, latestStory].filter(Boolean).map((story, index) => {
                      const date = getTimelineDate(story)
                      const label = index === 0 ? dictionary.coverageHub.firstReported : dictionary.coverageHub.latestUpdate

                      return (
                        <div key={`${label}-${story.id}`} className="rounded-editorial border border-[#ded2c0] bg-white/82 p-4 dark:border-white/10 dark:bg-[#182124]">
                          <div className="flex items-center gap-2 text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-primary-700 dark:text-primary-200">
                            <CalendarClock className="h-4 w-4" aria-hidden="true" />
                            {label}
                          </div>
                          <Link
                            href={`/story/${story.slug}`}
                            className="mt-2 block font-serif text-lg font-bold leading-tight text-ink transition-colors hover:text-primary-700 dark:text-[#fbf7f0] dark:hover:text-primary-200"
                          >
                            {getStoryHeadline(story, lang)}
                          </Link>
                          <p className="mt-2 text-sm leading-6 text-ink/62 dark:text-[#cfc8be]">
                            {story.source.name}
                            {' · '}
                            {date ? formatTimelineDate(date, lang) : dictionary.coverageHub.unknownDate}
                          </p>
                        </div>
                      )
                    })}
                  </div>

                  <div className="section-surface overflow-hidden">
                    <div className="divide-y divide-[#dfd4c3] dark:divide-white/10">
                      {timelineGroups.map((group) => (
                        <div key={group.key}>
                          <div className="bg-paper/80 px-5 py-3 text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-ink/50 dark:bg-[#141d1f] dark:text-[#b7b1a8] sm:px-6">
                            {group.date ? formatTimelineDate(group.date, lang) : dictionary.coverageHub.unknownDate}
                          </div>
                          <div className="divide-y divide-[#e7dccf] dark:divide-white/10">
                            {group.stories.map((story) => {
                              const date = getTimelineDate(story)
                              const isFirst = firstStory?.id === story.id
                              const isLatest = latestStory?.id === story.id
                              const timeLabel = date ? formatTimelineTime(date, lang) : dictionary.coverageHub.unknownTime

                              return (
                                <article key={story.id} className="grid gap-4 p-5 sm:grid-cols-[8.5rem_minmax(0,1fr)] sm:p-6">
                                  <div className="relative text-sm font-semibold text-ink/56 dark:text-[#bdb6ad]">
                                    <div className="flex items-center gap-2 sm:block">
                                      <span className="inline-flex min-w-[4.75rem] justify-center rounded-full border border-[#d8cab7] bg-white px-3 py-1.5 text-xs uppercase tracking-[0.12em] text-ink/62 dark:border-white/10 dark:bg-[#141d1f] dark:text-[#d9d3ca] sm:justify-start">
                                        {timeLabel}
                                      </span>
                                      {date ? (
                                        <span className="text-xs text-ink/42 dark:text-[#9d968d] sm:mt-2 sm:block">
                                          <TimeAgo date={story.publishedAt} />
                                        </span>
                                      ) : null}
                                    </div>
                                    <div className="mt-3 hidden min-h-[calc(100%-2rem)] border-l border-[#dfd4c3] pl-3 text-xs uppercase tracking-[0.14em] text-ink/40 dark:border-white/10 dark:text-[#9d968d] sm:block">
                                      {isFirst
                                        ? dictionary.coverageHub.firstReported
                                        : isLatest
                                          ? dictionary.coverageHub.latestUpdate
                                          : dictionary.coverageHub.relatedReport}
                                    </div>
                                  </div>
                                  <div>
                                    <div className="mb-3 flex flex-wrap items-center gap-2">
                                      <StoryLanguageBadge story={story} compact />
                                      <SourceBadge source={story.source} size="sm" />
                                      <span className="rounded-full border border-[#ded2c0] bg-paper px-2.5 py-1 text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-ink/50 dark:border-white/10 dark:bg-[#141d1f] dark:text-[#bdb6ad]">
                                        {dictionary.coverageHub.sourceLanguage}: {storyLanguageLabel(story)}
                                      </span>
                                      {storyRegionLabel(story) ? (
                                        <span className="rounded-full border border-[#ded2c0] bg-paper px-2.5 py-1 text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-ink/50 dark:border-white/10 dark:bg-[#141d1f] dark:text-[#bdb6ad]">
                                          {storyRegionLabel(story)}
                                        </span>
                                      ) : null}
                                    </div>
                                    <h3 className="font-serif text-xl font-bold leading-tight text-ink dark:text-[#fbf7f0]">
                                      <Link href={`/story/${story.slug}`} className="editorial-link hover:text-primary-700 dark:hover:text-primary-200">
                                        {getStoryHeadline(story, lang)}
                                      </Link>
                                    </h3>
                                    <p className="mt-2 text-sm leading-7 text-ink/70 dark:text-[#d8d2ca]">
                                      {getStoryExcerpt(story, lang)}
                                    </p>
                                    <dl className="mt-4 grid gap-2 text-xs leading-5 text-ink/56 dark:text-[#bdb6ad] sm:grid-cols-2">
                                      <div>
                                        <dt className="font-semibold uppercase tracking-[0.12em] text-ink/38 dark:text-[#9d968d]">
                                          {dictionary.coverageHub.sourceType}
                                        </dt>
                                        <dd className="mt-1 capitalize">{story.source.category || story.category || dictionary.coverageHub.sourceFallback}</dd>
                                      </div>
                                      <div>
                                        <dt className="font-semibold uppercase tracking-[0.12em] text-ink/38 dark:text-[#9d968d]">
                                          {dictionary.coverageHub.publishedAt}
                                        </dt>
                                        <dd className="mt-1">{date ? `${formatTimelineDate(date, lang)} · ${timeLabel}` : dictionary.coverageHub.unknownDate}</dd>
                                      </div>
                                    </dl>
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
                              )
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
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
