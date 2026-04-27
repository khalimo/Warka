import { ComparePageClient } from '@/components/pages/ComparePageClient'
import { CompareClusterLensFilters, apiClient } from '@/lib/api'

export const metadata = {
  title: 'Compare Coverage',
  description: 'See how different outlets cover the same story and where their reporting differs.',
}

export const dynamic = 'force-dynamic'

type PageProps = {
  searchParams?: {
    page?: string
    filter?: string
    language?: string
    source_category?: string
    confidence?: string
    recent?: string
    sources?: string
  }
}

const VALID_FILTERS = ['all', 'somalia', 'world', 'politics', 'security', 'humanitarian', 'economy'] as const
const VALID_LANGUAGES = ['all', 'so', 'en'] as const
const VALID_SOURCE_CATEGORIES = ['all', 'news', 'international', 'humanitarian', 'diaspora'] as const
const VALID_CONFIDENCE = ['all', 'high', 'medium', 'low'] as const
const VALID_RECENCY = ['all', '24', '72', '168'] as const
const VALID_SOURCE_COUNTS = ['all', '2plus', '3plus', '4plus'] as const

function normalizePage(rawPage?: string): number {
  const parsed = Number(rawPage)
  if (!Number.isFinite(parsed) || parsed < 1) {
    return 1
  }
  return Math.floor(parsed)
}

function normalizeFilter(rawFilter?: string): (typeof VALID_FILTERS)[number] {
  const normalized = (rawFilter || '').trim().toLowerCase()
  if (VALID_FILTERS.includes(normalized as (typeof VALID_FILTERS)[number])) {
    return normalized as (typeof VALID_FILTERS)[number]
  }
  return 'all'
}

function normalizeChoice<T extends readonly string[]>(rawValue: string | undefined, allowed: T): T[number] {
  const normalized = (rawValue || '').trim().toLowerCase()
  if (allowed.includes(normalized)) {
    return normalized as T[number]
  }
  return allowed[0]
}

export default async function ComparePage({ searchParams }: PageProps) {
  const page = normalizePage(searchParams?.page)
  const filter = normalizeFilter(searchParams?.filter)
  const language = normalizeChoice(searchParams?.language, VALID_LANGUAGES)
  const sourceCategory = normalizeChoice(searchParams?.source_category, VALID_SOURCE_CATEGORIES)
  const confidence = normalizeChoice(searchParams?.confidence, VALID_CONFIDENCE)
  const recent = normalizeChoice(searchParams?.recent, VALID_RECENCY)
  const sourceCount = normalizeChoice(searchParams?.sources, VALID_SOURCE_COUNTS)
  const limit = 20
  const offset = (page - 1) * limit
  const lensFilters: CompareClusterLensFilters = {
    language: language === 'all' ? undefined : language,
    sourceCategory: sourceCategory === 'all' ? undefined : sourceCategory,
    confidence: confidence === 'all' ? undefined : confidence,
    recentHours: recent === 'all' ? undefined : Number(recent),
    minSources: sourceCount === 'all' ? undefined : Number(sourceCount.replace('plus', '')),
  }
  const [result, sourceList, latest] = await Promise.all([
    apiClient.getCompareClusters(limit, offset, undefined, undefined, true, filter, lensFilters),
    apiClient.getSources(),
    apiClient.getLatestStories(12, 0),
  ])

  return (
    <ComparePageClient
      clusters={result?.items || []}
      total={result?.total || 0}
      limit={result?.limit || limit}
      offset={result?.offset || offset}
      activeSourceCount={sourceList?.length || 0}
      readyStoryCount={latest?.total || latest?.items.length || 0}
      apiUnavailable={!result}
      activeFilter={filter}
      activeLensFilters={{ language, sourceCategory, confidence, recent, sources: sourceCount }}
    />
  )
}
