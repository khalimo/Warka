'use client'

import Link from 'next/link'
import { CalendarDays, ExternalLink, GitCompareArrows, Languages, LucideIcon, Newspaper, ShieldCheck } from 'lucide-react'
import { CompareClusterCard } from '@/components/compare/CompareClusterCard'
import { SourceBadge } from '@/components/story/SourceBadge'
import { StoryLanguageBadge } from '@/components/story/StoryLanguageBadge'
import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { TimeAgo } from '@/components/ui/TimeAgo'
import { useLanguage } from '@/components/language/LanguageProvider'
import { languageMix, uniqueSources } from '@/lib/intelligence'
import { getStoryExcerpt, getStoryHeadline } from '@/lib/storyPresentation'
import { CompareCluster, HomePageData, Story } from '@/lib/types'

function uniqueStories(stories: Story[]) {
  const seen = new Set<string>()
  return stories.filter((story) => {
    if (seen.has(story.id)) return false
    seen.add(story.id)
    return true
  })
}

function isWithinHours(date: string, hours: number) {
  return Date.now() - new Date(date).getTime() <= hours * 60 * 60 * 1000
}

function storyMatchesRegional(story: Story) {
  const combined = `${story.region} ${story.category} ${story.source.category}`.toLowerCase()
  return ['horn', 'regional', 'africa', 'somaliland', 'puntland', 'humanitarian'].some((token) => combined.includes(token))
}

function storyMatchesWorldDiaspora(story: Story) {
  const combined = `${story.region} ${story.category} ${story.source.category}`.toLowerCase()
  return story.region === 'world' || ['diaspora', 'international', 'world', 'global'].some((token) => combined.includes(token))
}

function formatBriefingDate(lang: string) {
  return new Intl.DateTimeFormat(lang === 'so' ? 'so-SO' : 'en-GB', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date())
}

function confidenceLabel(cluster: CompareCluster, dictionary: ReturnType<typeof useLanguage>['dictionary']) {
  const confidence = cluster.confidenceScore ?? cluster.eventSignature?.confidence ?? 0
  if (!confidence) return dictionary.trustMethodology.confidenceNew
  if (confidence >= 75) return `${confidence} ${dictionary.sourceLens.high}`
  if (confidence >= 50) return `${confidence} ${dictionary.sourceLens.medium}`
  return `${confidence} ${dictionary.sourceLens.low}`
}

function BriefingStoryItem({ story }: { story: Story }) {
  const { lang, dictionary } = useLanguage()

  return (
    <article className="rounded-editorial border border-[#ded2c0] bg-white/86 p-4 shadow-sm dark:border-white/10 dark:bg-[#182124] sm:p-5">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <StoryLanguageBadge story={story} compact />
        <SourceBadge source={story.source} size="sm" />
        <span className="rounded-full border border-[#ded2c0] bg-paper/70 px-2.5 py-1 text-xs font-semibold text-ink/58 dark:border-white/10 dark:bg-[#141d1f] dark:text-[#cfc8bf]">
          <TimeAgo date={story.publishedAt} />
        </span>
      </div>
      <h3 className="font-serif text-xl font-bold leading-tight text-ink dark:text-[#fbf7f0]">
        <Link href={`/story/${story.slug}`} className="editorial-link hover:text-primary-700 dark:hover:text-primary-200">
          {getStoryHeadline(story, lang)}
        </Link>
      </h3>
      <p className="mt-2 line-clamp-3 text-sm leading-7 text-ink/70 dark:text-[#d8d2ca]">
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
    </article>
  )
}

function BriefingClusterItem({ cluster }: { cluster: CompareCluster }) {
  const { dictionary } = useLanguage()
  const sources = cluster.sources.length || cluster.eventSignature?.source_count || 0
  const mix = languageMix(cluster.stories, dictionary)

  return (
    <article className="rounded-editorial border border-[#ded2c0] bg-white/86 p-4 shadow-sm dark:border-white/10 dark:bg-[#182124] sm:p-5">
      <div className="mb-3 flex flex-wrap gap-2">
        <span className="signature-chip">{dictionary.coverageHub.kicker}</span>
        <span className="rounded-full border border-[#ded2c0] bg-paper/70 px-2.5 py-1 text-xs font-semibold text-ink/62 dark:border-white/10 dark:bg-[#141d1f] dark:text-[#d9d3ca]">
          {confidenceLabel(cluster, dictionary)}
        </span>
      </div>
      <h3 className="font-serif text-xl font-bold leading-tight text-ink dark:text-[#fbf7f0]">
        <Link href={`/compare/${encodeURIComponent(cluster.id)}`} className="editorial-link hover:text-primary-700 dark:hover:text-primary-200">
          {cluster.title}
        </Link>
      </h3>
      <p className="mt-2 line-clamp-3 text-sm leading-7 text-ink/70 dark:text-[#d8d2ca]">
        {cluster.aiNeutralSummary || cluster.neutralSummary || cluster.commonFacts || dictionary.compare.developing}
      </p>
      <div className="mt-4 grid gap-2 sm:grid-cols-3">
        {[
          [dictionary.compare.sourceCount, sources],
          [dictionary.compare.languageMix, mix],
          [dictionary.compare.storyCount, cluster.stories.length],
        ].map(([label, value]) => (
          <div key={label} className="rounded-editorial border border-[#ded2c0] bg-paper/70 px-3 py-2 dark:border-white/10 dark:bg-[#141d1f]">
            <div className="text-[0.64rem] font-semibold uppercase tracking-[0.12em] text-ink/45 dark:text-[#aaa39a]">{label}</div>
            <div className="mt-1 text-sm font-semibold text-ink/78 dark:text-[#e0dbd2]">{value}</div>
          </div>
        ))}
      </div>
      <Link
        href={`/compare/${encodeURIComponent(cluster.id)}`}
        className="mt-4 inline-flex min-h-[40px] items-center rounded-full border border-primary-200 bg-primary-50 px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-primary-700 transition-colors hover:bg-primary-100 dark:border-primary-900/50 dark:bg-primary-900/20 dark:text-primary-200"
      >
        {dictionary.coverageHub.openFullCoverage}
      </Link>
    </article>
  )
}

function Rail({ title, stories }: { title: string; stories: Story[] }) {
  if (stories.length === 0) return null

  return (
    <section>
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-[0.16em] text-ink/58 dark:text-[#bbb4ab]">
        {title}
      </h2>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {stories.slice(0, 3).map((story) => (
          <BriefingStoryItem key={story.id} story={story} />
        ))}
      </div>
    </section>
  )
}

export function BriefingPageClient({
  homeData,
  clusters,
  latestStories,
  activeSourceCount,
  apiUnavailable = false,
}: {
  homeData: HomePageData | null
  clusters: CompareCluster[]
  latestStories: Story[]
  activeSourceCount: number
  apiUnavailable?: boolean
}) {
  const { lang, dictionary } = useLanguage()
  const topStories = uniqueStories([
    ...(homeData ? [homeData.heroStory, ...homeData.secondaryStories] : []),
    ...latestStories,
  ]).slice(0, 5)
  const storiesLast24h = latestStories.filter((story) => isWithinHours(story.publishedAt, 24))
  const storiesLast48h = latestStories.filter((story) => isWithinHours(story.publishedAt, 48))
  const newSinceYesterday = Math.max(0, storiesLast24h.length)
  const changedSources = uniqueSources(storiesLast24h)
  const changedCategories = Array.from(new Set(storiesLast24h.map((story) => story.category).filter(Boolean))).slice(0, 4)
  const somaliaStories = latestStories.filter((story) => story.region === 'somalia').slice(0, 3)
  const regionalStories = latestStories.filter(storyMatchesRegional).slice(0, 3)
  const worldDiasporaStories = latestStories.filter(storyMatchesWorldDiaspora).slice(0, 3)
  const languageSummary = languageMix(topStories.length > 0 ? topStories : latestStories, dictionary)
  const snapshotStats: Array<{ label: string; value: string | number; Icon: LucideIcon }> = [
    { label: dictionary.briefingPage.topStories, value: topStories.length, Icon: Newspaper },
    { label: dictionary.briefingPage.activeClusters, value: clusters.length, Icon: GitCompareArrows },
    { label: dictionary.compare.activeSources, value: activeSourceCount, Icon: ShieldCheck },
    { label: dictionary.compare.languageMix, value: languageSummary, Icon: Languages },
  ]

  if (apiUnavailable || (topStories.length === 0 && clusters.length === 0)) {
    return (
      <div className="bg-paper dark:bg-[#141b1d]">
        <section className="container-custom py-16 md:py-20">
          <EmptyState
            title={dictionary.briefingPage.emptyTitle}
            message={dictionary.briefingPage.emptyMessage}
          />
        </section>
      </div>
    )
  }

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <section className="border-b news-divider">
        <div className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
          <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-end">
            <div>
              <div className="mb-4 flex flex-wrap items-center gap-3">
                <span className="signature-chip">{dictionary.briefingPage.kicker}</span>
                <span className="inline-flex items-center gap-2 text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-ink/50 dark:text-[#b7b1a8]">
                  <CalendarDays className="h-4 w-4" />
                  {formatBriefingDate(lang)}
                </span>
              </div>
              <h1 className="max-w-[15ch] text-[2.55rem] font-bold leading-[0.96] text-ink dark:text-[#fbf7f0] sm:text-[3.7rem] lg:text-[4.5rem]">
                {dictionary.briefingPage.title}
              </h1>
              <p className="mt-6 max-w-3xl text-base leading-8 text-ink/72 dark:text-[#d8d2ca] sm:text-lg">
                {dictionary.briefingPage.deck}
              </p>
            </div>

            <aside className="section-surface p-5">
              <div className="eyebrow">{dictionary.briefingPage.snapshot}</div>
              <div className="mt-4 grid gap-3">
                {snapshotStats.map(({ label, value, Icon }) => (
                  <div key={label} className="flex items-center gap-3 rounded-editorial border border-[#ded2c0] bg-paper/70 p-3 dark:border-white/10 dark:bg-[#141d1f]">
                    <span className="flex h-9 w-9 items-center justify-center rounded-full border border-primary-200 bg-primary-50 text-primary-700 dark:border-primary-900/60 dark:bg-primary-900/20 dark:text-primary-200">
                      <Icon className="h-4 w-4" />
                    </span>
                    <div>
                      <div className="text-[0.64rem] font-semibold uppercase tracking-[0.12em] text-ink/45 dark:text-[#aaa39a]">{label}</div>
                      <div className="text-lg font-bold text-ink dark:text-[#fbf7f0]">{value}</div>
                    </div>
                  </div>
                ))}
              </div>
            </aside>
          </div>
        </div>
      </section>

      <section className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
        <div className="mx-auto max-w-6xl space-y-12">
          <section>
            <SectionHeader
              title={dictionary.briefingPage.developmentsTitle}
              subtitle={dictionary.briefingPage.developmentsSubtitle}
            />
            {topStories.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2">
                {topStories.map((story) => (
                  <BriefingStoryItem key={story.id} story={story} />
                ))}
              </div>
            ) : (
              <EmptyState title={dictionary.pages.latest.emptyTitle} message={dictionary.pages.latest.emptyMessage} />
            )}
          </section>

          <section>
            <SectionHeader
              title={dictionary.briefingPage.clustersTitle}
              subtitle={dictionary.briefingPage.clustersSubtitle}
            />
            {clusters.length > 0 ? (
              <div className="space-y-6">
                <div className="grid gap-4 lg:grid-cols-2">
                  {clusters.slice(0, 4).map((cluster) => (
                    <BriefingClusterItem key={cluster.id} cluster={cluster} />
                  ))}
                </div>
                <div className="pt-2">
                  <CompareClusterCard cluster={clusters[0]} />
                </div>
              </div>
            ) : (
              <EmptyState title={dictionary.compare.watchTitle} message={dictionary.compare.watchMessage} />
            )}
          </section>

          <section className="section-surface p-5 sm:p-6">
            <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:items-start">
              <div>
                <div className="eyebrow">{dictionary.briefingPage.changedKicker}</div>
                <h2 className="mt-2 text-2xl font-bold text-ink dark:text-[#fbf7f0]">
                  {dictionary.briefingPage.changedTitle}
                </h2>
                <p className="mt-3 text-sm leading-7 text-ink/68 dark:text-[#d8d2ca]">
                  {newSinceYesterday > 0
                    ? dictionary.briefingPage.changedMessage
                        .replace('{count}', String(newSinceYesterday))
                        .replace('{sources}', String(changedSources.length))
                    : dictionary.briefingPage.noChangedMessage}
                </p>
              </div>
              <div className="grid gap-3 sm:grid-cols-3">
                {[
                  [dictionary.briefingPage.last24h, newSinceYesterday],
                  [dictionary.briefingPage.last48h, storiesLast48h.length],
                  [dictionary.pages.sources.categories, changedCategories.length || 0],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-editorial border border-[#ded2c0] bg-paper/70 px-4 py-3 dark:border-white/10 dark:bg-[#141d1f]">
                    <div className="font-serif text-3xl font-bold text-ink dark:text-[#fbf7f0]">{value}</div>
                    <div className="mt-1 text-[0.68rem] font-semibold uppercase tracking-[0.12em] text-ink/45 dark:text-[#aaa39a]">{label}</div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <div className="space-y-10">
            <Rail title={dictionary.briefingPage.somaliaTitle} stories={somaliaStories} />
            <Rail title={dictionary.briefingPage.regionalTitle} stories={regionalStories} />
            <Rail title={dictionary.briefingPage.worldDiasporaTitle} stories={worldDiasporaStories} />
          </div>
        </div>
      </section>
    </div>
  )
}
