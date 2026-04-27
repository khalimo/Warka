'use client'

import { ChevronDown, Sparkles, ShieldCheck } from 'lucide-react'
import type { ReactNode } from 'react'
import { AppLanguage, UIStrings } from '@/lib/i18n'
import { CompareCluster, Story } from '@/lib/types'

type TrustItem = {
  label: string
  value: string
}

function languageName(lang: string, dictionary: UIStrings) {
  return lang === 'so' ? dictionary.languages.so : dictionary.languages.en
}

function languageMix(stories: Story[], dictionary: UIStrings) {
  const languages = Array.from(new Set(stories.map((story) => story.lang))).filter(Boolean)
  if (languages.length === 0) {
    return dictionary.trustMethodology.unknown
  }
  return languages.map((lang) => languageName(lang, dictionary)).join(' + ')
}

function confidenceLabel(score: number | undefined, dictionary: UIStrings) {
  if (!score) {
    return dictionary.trustMethodology.confidenceNew
  }
  if (score >= 75) {
    return dictionary.trustMethodology.confidenceHigh
  }
  if (score >= 50) {
    return dictionary.trustMethodology.confidenceMedium
  }
  return dictionary.trustMethodology.confidenceLow
}

function storyTranslationStatus(story: Story, lang: AppLanguage, dictionary: UIStrings) {
  if (story.lang === lang) {
    return dictionary.trustMethodology.translationOriginal
  }
  if (story.translations?.headline?.[lang] || story.translations?.summary?.[lang] || story.translations?.content?.[lang]) {
    return dictionary.trustMethodology.translationAvailable
  }
  return dictionary.trustMethodology.translationUnavailable
}

function clusterTranslationStatus(cluster: CompareCluster, lang: AppLanguage, dictionary: UIStrings) {
  const translatedCount = cluster.stories.filter((story) => (
    story.lang !== lang
    && (story.translations?.headline?.[lang] || story.translations?.summary?.[lang] || story.translations?.content?.[lang])
  )).length

  if (translatedCount > 0) {
    return dictionary.trustMethodology.clusterTranslationAvailable
  }
  return dictionary.trustMethodology.clusterTranslationMixed
}

function sourceNames(sources: Array<{ name: string }>, dictionary: UIStrings) {
  if (sources.length === 0) {
    return dictionary.trustMethodology.unknown
  }
  return sources.slice(0, 4).map((source) => source.name).join(', ')
}

function publicClusterSignals(cluster: CompareCluster, dictionary: UIStrings) {
  const terms = cluster.eventSignature?.event_terms || cluster.keyThemes || []
  const entities = cluster.eventSignature?.entities || []
  const signals = [...terms, ...entities]
    .map((signal) => String(signal).trim())
    .filter(Boolean)

  if (typeof cluster.eventSignature?.temporal_span_hours === 'number') {
    signals.push(`${dictionary.compare.timeWindow}: ${cluster.eventSignature.temporal_span_hours}h`)
  }

  return Array.from(new Set(signals)).slice(0, 8)
}

function DetailGrid({ items }: { items: TrustItem[] }) {
  return (
    <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((item) => (
        <div
          key={item.label}
          className="rounded-editorial border border-[#ded2c0] bg-white/70 px-4 py-3 dark:border-white/10 dark:bg-[#141d1f]"
        >
          <dt className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#aaa39a]">
            {item.label}
          </dt>
          <dd className="mt-1 text-sm font-medium leading-6 text-ink/78 dark:text-[#e0dbd2]">
            {item.value}
          </dd>
        </div>
      ))}
    </dl>
  )
}

export function StoryTrustMethodologyPanel({
  story,
  lang,
  dictionary,
}: {
  story: Story
  lang: AppLanguage
  dictionary: UIStrings
}) {
  const items: TrustItem[] = [
    { label: dictionary.trustMethodology.sourceCount, value: '1' },
    { label: dictionary.trustMethodology.sourcesUsed, value: story.source.name },
    { label: dictionary.trustMethodology.languageMix, value: languageName(story.lang, dictionary) },
    { label: dictionary.trustMethodology.translationStatus, value: storyTranslationStatus(story, lang, dictionary) },
    { label: dictionary.trustMethodology.confidence, value: dictionary.trustMethodology.singleStoryConfidence },
    { label: dictionary.trustMethodology.aiSynthesis, value: dictionary.trustMethodology.aiNotUsedStory },
  ]
  const signals = [story.region, story.category, ...(story.topics || [])].filter(Boolean).slice(0, 6)

  return (
    <TrustShell
      eyebrow={dictionary.trustMethodology.storyEyebrow}
      title={dictionary.trustMethodology.storyTitle}
      summary={dictionary.trustMethodology.storyWhy}
    >
      <DetailGrid items={items} />
      {signals.length > 0 ? <SignalList label={dictionary.trustMethodology.signalsUsed} signals={signals} /> : null}
    </TrustShell>
  )
}

export function ClusterTrustMethodologyPanel({
  cluster,
  lang,
  dictionary,
}: {
  cluster: CompareCluster
  lang: AppLanguage
  dictionary: UIStrings
}) {
  const confidence = cluster.confidenceScore ?? cluster.eventSignature?.confidence
  const items: TrustItem[] = [
    { label: dictionary.trustMethodology.sourceCount, value: String(cluster.sources.length || cluster.eventSignature?.source_count || 0) },
    { label: dictionary.trustMethodology.sourcesUsed, value: sourceNames(cluster.sources, dictionary) },
    { label: dictionary.trustMethodology.languageMix, value: languageMix(cluster.stories, dictionary) },
    { label: dictionary.trustMethodology.translationStatus, value: clusterTranslationStatus(cluster, lang, dictionary) },
    { label: dictionary.trustMethodology.confidence, value: `${confidence || dictionary.trustMethodology.confidenceNew} ${confidence ? confidenceLabel(confidence, dictionary) : ''}`.trim() },
    { label: dictionary.trustMethodology.aiSynthesis, value: cluster.hasAISynthesis ? dictionary.trustMethodology.aiUsed : dictionary.trustMethodology.aiNotUsedCluster },
  ]
  const signals = publicClusterSignals(cluster, dictionary)

  return (
    <TrustShell
      eyebrow={dictionary.trustMethodology.clusterEyebrow}
      title={dictionary.trustMethodology.clusterTitle}
      summary={dictionary.trustMethodology.clusterWhy}
    >
      <DetailGrid items={items} />
      <div className="rounded-editorial border border-acacia/25 bg-acacia/10 p-4 text-sm leading-7 text-ink/74 dark:border-acacia/20 dark:bg-acacia/10 dark:text-[#ded8cf]">
        {dictionary.trustMethodology.confidenceExplainer}
      </div>
      {signals.length > 0 ? <SignalList label={dictionary.trustMethodology.signalsUsed} signals={signals} /> : null}
    </TrustShell>
  )
}

function SignalList({ label, signals }: { label: string; signals: string[] }) {
  return (
    <div>
      <div className="mb-2 text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-ink/50 dark:text-[#aaa39a]">
        {label}
      </div>
      <div className="flex flex-wrap gap-2">
        {signals.map((signal) => (
          <span
            key={signal}
            className="rounded-full border border-[#ded2c0] bg-paper/70 px-2.5 py-1 text-xs font-semibold text-ink/68 dark:border-white/10 dark:bg-[#141d1f] dark:text-[#d9d3ca]"
          >
            {signal}
          </span>
        ))}
      </div>
    </div>
  )
}

function TrustShell({
  eyebrow,
  title,
  summary,
  children,
}: {
  eyebrow: string
  title: string
  summary: string
  children: ReactNode
}) {
  return (
    <details className="group overflow-hidden rounded-editorial border border-[#d8cab7] bg-white/82 shadow-lift dark:border-white/10 dark:bg-[#182124]">
      <summary className="flex cursor-pointer list-none items-start justify-between gap-4 p-4 marker:hidden sm:p-5">
        <div className="flex gap-3">
          <span className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-editorial border border-primary-200 bg-primary-50 text-primary-700 dark:border-primary-900/60 dark:bg-primary-900/20 dark:text-primary-200">
            <ShieldCheck className="h-4 w-4" />
          </span>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="eyebrow">{eyebrow}</span>
              <Sparkles className="h-3.5 w-3.5 text-acacia" />
            </div>
            <h3 className="mt-1 text-lg font-bold leading-tight text-ink dark:text-[#fbf7f0]">{title}</h3>
            <p className="mt-2 text-sm leading-6 text-ink/68 dark:text-[#d8d2ca]">{summary}</p>
          </div>
        </div>
        <ChevronDown className="mt-2 h-5 w-5 shrink-0 text-ink/45 transition-transform group-open:rotate-180 dark:text-[#aaa39a]" />
      </summary>
      <div className="space-y-4 border-t news-divider px-4 pb-5 pt-4 sm:px-5">
        {children}
      </div>
    </details>
  )
}
