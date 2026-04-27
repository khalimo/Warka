'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { CompareCluster } from '@/lib/types'
import { SourceBadge } from '@/components/story/SourceBadge'
import { StoryLanguageBadge } from '@/components/story/StoryLanguageBadge'
import { ClusterTrustMethodologyPanel } from '@/components/trust/TrustMethodologyPanel'
import { useLanguage } from '@/components/language/LanguageProvider'
import { getCompareSourceStats } from '@/lib/intelligence'
import { getStoryExcerpt, getStoryHeadline } from '@/lib/storyPresentation'

interface CompareClusterCardProps {
  cluster: CompareCluster
}

export function CompareClusterCard({ cluster }: CompareClusterCardProps) {
  const [expanded, setExpanded] = useState(false)
  const { lang, dictionary } = useLanguage()
  const somaliStory = cluster.stories.find((story) => story.lang === 'so')
  const englishStory = cluster.stories.find((story) => story.lang === 'en')
  const comparisonStories = (
    somaliStory && englishStory ? [somaliStory, englishStory] : cluster.stories.slice(0, 2)
  ).filter((story): story is CompareCluster['stories'][number] => Boolean(story))
  const summary = cluster.aiNeutralSummary || cluster.neutralSummary || cluster.commonFacts
  const differences = cluster.aiCoverageDifferences || cluster.coverageDifferences || dictionary.compare.developing
  const sourceStats = getCompareSourceStats(cluster, dictionary)
  const confidence = cluster.confidenceScore ?? cluster.eventSignature?.confidence ?? 0
  const eventTerms = (cluster.eventSignature?.event_terms || cluster.keyThemes || []).slice(0, 5)
  const timeWindow = cluster.eventSignature?.temporal_span_hours
  const confidenceTone =
    confidence >= 75
      ? 'border-emerald-500/30 bg-emerald-50 text-emerald-800 dark:border-emerald-300/20 dark:bg-emerald-300/10 dark:text-emerald-100'
      : confidence >= 50
        ? 'border-acacia/30 bg-acacia/10 text-acacia dark:border-acacia/20 dark:bg-acacia/10 dark:text-acacia'
        : 'border-[#ded2c0] bg-paper/70 text-ink/72 dark:border-white/10 dark:bg-[#141d1f] dark:text-[#d9d3ca]'

  return (
    <div className="overflow-hidden rounded-editorial border border-[#dccfbe] bg-white/92 shadow-lift transition duration-300 ease-editorial hover:shadow-editorial dark:border-white/10 dark:bg-[#182124]">
      <div className="p-5 sm:p-6 md:p-7">
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <span className="signature-chip">{dictionary.sections.compareCoverage}</span>
          <span className="text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-ink/45 dark:text-[#b7b1a8]">
            {dictionary.compare.kicker}
          </span>
        </div>
        <h3 className="text-[1.45rem] font-bold leading-tight text-ink dark:text-[#fbf7f0] sm:text-2xl">{cluster.title}</h3>

        <div className="mt-5 space-y-4 sm:mt-6 sm:space-y-5">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {sourceStats.map((item) => (
              <div
                key={item.label}
                className="rounded-editorial border border-[#ded2c0] bg-paper/70 px-4 py-3 dark:border-white/10 dark:bg-[#141d1f]"
              >
                <div className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/48 dark:text-[#b7b1a8]">
                  {item.label}
                </div>
                <div className="mt-1 font-serif text-[1.35rem] font-bold leading-none text-ink dark:text-[#fbf7f0]">
                  {item.value}
                </div>
              </div>
            ))}
            <div
              className={`rounded-editorial border px-4 py-3 ${confidenceTone}`}
            >
              <div className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] opacity-70">
                {dictionary.compare.clusterConfidence}
              </div>
              <div className="mt-1 font-serif text-[1.35rem] font-bold leading-none">
                {confidence || 'New'}
              </div>
            </div>
          </div>

          <div className="rounded-editorial border border-acacia/25 bg-acacia/10 p-4 dark:border-acacia/20 dark:bg-acacia/10">
            <h4 className="mb-2 text-sm font-semibold uppercase tracking-[0.14em] text-acacia">
              {dictionary.compare.agreement}
            </h4>
            <p className="text-sm leading-7 text-ink/78 dark:text-[#e2ddd5]">{summary}</p>
          </div>

          {comparisonStories.length > 0 ? (
            <div className="-mx-5 flex snap-x gap-4 overflow-x-auto px-5 pb-1 sm:-mx-6 sm:px-6 md:mx-0 md:grid md:grid-cols-2 md:overflow-visible md:px-0">
              {comparisonStories.map((story) => (
                <div
                  key={story.id}
                  className="min-w-[82%] snap-start rounded-editorial border border-[#ded2c0] bg-paper/80 p-4 dark:border-white/10 dark:bg-[#141d1f] sm:min-w-[68%] md:min-w-0"
                >
                  <div className="mb-3 flex flex-wrap items-center gap-2">
                    <StoryLanguageBadge story={story} compact />
                    <SourceBadge source={story.source} size="sm" />
                  </div>
                  <h4 className="font-serif text-[1.08rem] font-bold leading-[1.16] text-ink dark:text-[#fbf7f0]">
                    {getStoryHeadline(story, lang)}
                  </h4>
                  <p className="mt-2 line-clamp-4 text-sm leading-7 text-ink/72 dark:text-[#d9d3ca]">
                    {getStoryExcerpt(story, lang)}
                  </p>
                </div>
              ))}
            </div>
          ) : null}

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_15rem] lg:items-start">
            <div>
              <h4 className="mb-2 text-sm font-semibold uppercase tracking-[0.14em] text-ink/60 dark:text-[#bbb4ab]">
                {dictionary.compare.differences}
              </h4>
              <p className="text-sm leading-7 text-ink/74 dark:text-[#d9d3ca]">{differences}</p>
            </div>

            <div>
              <div className="space-y-4">
                <div>
                  <h4 className="mb-2 text-sm font-semibold uppercase tracking-[0.14em] text-ink/60 dark:text-[#bbb4ab]">
                    {dictionary.compare.trustTitle}
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {cluster.sources.map((source) => (
                      <SourceBadge key={source.id} source={source} size="sm" />
                    ))}
                  </div>
                </div>
                {eventTerms.length > 0 || typeof timeWindow === 'number' ? (
                  <div>
                    <h4 className="mb-2 text-sm font-semibold uppercase tracking-[0.14em] text-ink/60 dark:text-[#bbb4ab]">
                      {dictionary.compare.eventSignals}
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {eventTerms.map((term) => (
                        <span
                          key={term}
                          className="rounded-full border border-[#ded2c0] bg-paper/70 px-2.5 py-1 text-xs font-semibold text-ink/68 dark:border-white/10 dark:bg-[#141d1f] dark:text-[#d9d3ca]"
                        >
                          {term}
                        </span>
                      ))}
                      {typeof timeWindow === 'number' ? (
                        <span className="rounded-full border border-[#ded2c0] bg-paper/70 px-2.5 py-1 text-xs font-semibold text-ink/68 dark:border-white/10 dark:bg-[#141d1f] dark:text-[#d9d3ca]">
                          {dictionary.compare.timeWindow}: {timeWindow}h
                        </span>
                      ) : null}
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </div>

          <ClusterTrustMethodologyPanel cluster={cluster} lang={lang} dictionary={dictionary} />

          <Link
            href={`/compare/${encodeURIComponent(cluster.id)}`}
            className="inline-flex min-h-[44px] items-center justify-center rounded-full border border-primary-200 bg-primary-50 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.14em] text-primary-700 transition-colors duration-300 ease-editorial hover:bg-primary-100 dark:border-primary-900/50 dark:bg-primary-900/20 dark:text-primary-200 dark:hover:bg-primary-900/30"
          >
            {dictionary.coverageHub.openFullCoverage}
          </Link>

          <button
            onClick={() => setExpanded((value) => !value)}
            className="inline-flex min-h-[44px] items-center gap-2 text-sm font-semibold uppercase tracking-[0.14em] text-primary-600 transition-colors duration-300 ease-editorial hover:text-primary-700 dark:text-primary-200 dark:hover:text-primary-100"
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            {expanded
              ? dictionary.compare.hideStories
              : `${dictionary.compare.viewStories} (${cluster.stories.length})`}
          </button>

          {expanded ? (
            <div className="space-y-3 border-t news-divider pt-5">
              {cluster.stories.map((story) => (
                <Link
                  key={story.id}
                  href={`/story/${story.slug}`}
                  className="block rounded-editorial border border-transparent p-3 transition-colors duration-300 ease-editorial hover:border-[#d9ccba] hover:bg-paper dark:hover:border-white/10 dark:hover:bg-[#1d2629]"
                >
                  <h5 className="font-serif text-lg font-bold text-ink dark:text-[#fbf7f0]">
                    {getStoryHeadline(story, lang)}
                  </h5>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <StoryLanguageBadge story={story} compact />
                    <SourceBadge source={story.source} size="sm" />
                  </div>
                </Link>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
