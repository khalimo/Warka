import {
  AIReviewUpdateResponse,
  BackendAIReviewUpdateResponse,
  BackendCluster,
  BackendHomePageData,
  BackendOperationsSummary,
  BackendSource,
  BackendStory,
  CompareCluster,
  HomePageData,
  OperationsSummary,
  PaginatedResponse,
  Source,
  Story,
} from './types'
import { AppLanguage } from './i18n'

function getCategoryImage(category?: string | null): string {
  const placeholders: Record<string, string> = {
    politics: '/images/politics-placeholder.svg',
    security: '/images/security-placeholder.svg',
    economy: '/images/economy-placeholder.svg',
    humanitarian: '/images/humanitarian-placeholder.svg',
    diaspora: '/images/diaspora-placeholder.svg',
    default: '/images/default-placeholder.svg',
  }

  const normalized = (category || '').toLowerCase()
  return placeholders[normalized] || placeholders.default
}

function mapFramingTone(
  tone?: string | null
): 'positive' | 'neutral' | 'negative' | 'mixed' {
  if (tone === 'positive' || tone === 'neutral' || tone === 'negative' || tone === 'mixed') {
    return tone
  }
  return 'neutral'
}

function detectStoryLanguage(story: BackendStory): AppLanguage {
  const sourceLanguage = story.source.language?.toLowerCase()

  if (sourceLanguage?.startsWith('so')) {
    return 'so'
  }

  if (sourceLanguage?.startsWith('en')) {
    return 'en'
  }

  const combinedText = `${story.title} ${story.excerpt || ''} ${story.summary || ''}`.toLowerCase()
  const somaliSignals = [
    'ayaa',
    'soomaaliya',
    'muqdisho',
    'wasaaradda',
    'wasiir',
    'dadka',
    'gobolka',
    'ciidamada',
    'warbixin',
    'maanta',
    'kadib',
    'qorshe',
    'cusub',
  ]

  const englishSignals = [
    'the ',
    'somalia',
    'government',
    'minister',
    'report',
    'president',
    'world',
    'after',
    'security',
    'economy',
  ]

  const somaliMatches = somaliSignals.filter((signal) => combinedText.includes(signal)).length
  const englishMatches = englishSignals.filter((signal) => combinedText.includes(signal)).length

  if (somaliMatches > englishMatches) {
    return 'so'
  }

  return 'en'
}

export function mapSource(source: BackendSource): Source {
  return {
    id: source.id,
    name: source.name,
    url: source.base_url || source.feed_url || '',
    category: source.category,
    description: source.description,
    language: source.language || undefined,
    country: source.country || undefined,
    isActive: source.is_active,
    lastSuccessAt: source.last_success_at || undefined,
  }
}

export function mapStory(story: BackendStory): Story {
  return {
    id: story.id,
    slug: story.slug,
    lang: detectStoryLanguage(story),
    title: story.title,
    excerpt: story.excerpt || story.summary || '',
    content: story.content_html || undefined,
    summary: story.summary || undefined,
    translations: story.translations || undefined,
    source: mapSource(story.source),
    publishedAt: story.published_at,
    updatedAt: story.updated_at || undefined,
    region: story.region,
    category: story.category,
    topics: story.topics || [],
    framing: story.framing
      ? {
          id: story.framing.id,
          label: story.framing.label,
          description: story.framing.description,
          tone: mapFramingTone(story.framing.tone),
        }
      : undefined,
    imageUrl: story.image_url || getCategoryImage(story.category),
    originalUrl: story.original_url,
    readingTime: story.reading_time || undefined,
    clusterId: story.cluster_id || undefined,
    isBreaking: story.is_breaking,
  }
}

export function mapCluster(cluster: BackendCluster): CompareCluster {
  const stories = cluster.stories || []
  const sources = cluster.sources || []

  return {
    id: cluster.id,
    title: cluster.title,
    commonFacts: cluster.common_facts || '',
    coverageDifferences:
      cluster.coverage_differences || 'Coverage differences are still being enriched for this story.',
    neutralSummary: cluster.neutral_summary || '',
    keyThemes: cluster.key_themes || [],
    consensusLevel: cluster.consensus_level,
    aiNeutralSummary: cluster.ai_neutral_summary || undefined,
    aiCoverageDifferences: cluster.ai_coverage_differences || undefined,
    aiConsensusLevel: cluster.ai_consensus_level || undefined,
    aiKeyThemes: cluster.ai_key_themes || [],
    aiGeneratedAt: cluster.ai_generated_at || undefined,
    aiModelUsed: cluster.ai_model_used || undefined,
    hasAISynthesis: cluster.has_ai_synthesis || false,
    aiReviewStatus: cluster.ai_review_status || 'unreviewed',
    aiReviewNote: cluster.ai_review_note || undefined,
    aiReviewedAt: cluster.ai_reviewed_at || undefined,
    createdAt: cluster.created_at || undefined,
    updatedAt: cluster.updated_at || undefined,
    storyCount: cluster.story_count || undefined,
    confidenceScore: cluster.confidence_score ?? undefined,
    eventSignature: cluster.event_signature || undefined,
    stories: stories.map(mapStory),
    sources: sources.map(mapSource),
  }
}

export function mapHomePageData(home: BackendHomePageData): HomePageData {
  const compareClusters = (home.compare_clusters || []).map(mapCluster)
  const diagnostics = home.diagnostics || {}

  return {
    heroStory: mapStory(home.hero_story),
    secondaryStories: home.secondary_stories.map(mapStory),
    comparePreview: home.compare_preview ? mapCluster(home.compare_preview) : null,
    compareClusters,
    diagnostics: {
      storyCount: diagnostics.story_count || 0,
      activeSourceCount: diagnostics.active_source_count || 0,
      totalClusterCount: diagnostics.total_cluster_count || 0,
      renderableClusterCount: diagnostics.renderable_cluster_count || 0,
      latestClusterCreatedAt: diagnostics.latest_cluster_created_at || undefined,
    },
    latestStories: home.latest_stories.map(mapStory),
    somaliaStories: home.somalia_stories.map(mapStory),
    worldStories: home.world_stories.map(mapStory),
  }
}

export function mapPaginatedStories(
  response: PaginatedResponse<BackendStory>
): PaginatedResponse<Story> {
  return {
    items: response.items.map(mapStory),
    total: response.total,
    limit: response.limit,
    offset: response.offset,
  }
}

export function mapPaginatedClusters(
  response: PaginatedResponse<BackendCluster>
): PaginatedResponse<CompareCluster> {
  return {
    items: response.items.map(mapCluster),
    total: response.total,
    limit: response.limit,
    offset: response.offset,
  }
}

export function mapAIReviewUpdateResponse(
  response: BackendAIReviewUpdateResponse
): AIReviewUpdateResponse {
  return {
    clusterId: response.cluster_id,
    aiReviewStatus: response.ai_review_status,
    aiReviewNote: response.ai_review_note || undefined,
    aiReviewedAt: response.ai_reviewed_at || undefined,
  }
}

export function mapOperationsSummary(summary: BackendOperationsSummary): OperationsSummary {
  return {
    status: summary.status,
    generatedAt: summary.generated_at,
    storyCount: summary.story_count,
    clusterCount: summary.cluster_count,
    sourceCount: summary.source_count,
    activeSourceCount: summary.active_source_count,
    translatedStorySampleCount: summary.translated_story_sample_count,
    latestIngestRun: summary.latest_ingest_run
      ? {
          id: summary.latest_ingest_run.id,
          startedAt: summary.latest_ingest_run.started_at,
          completedAt: summary.latest_ingest_run.completed_at || undefined,
          status: summary.latest_ingest_run.status,
          processedCount: summary.latest_ingest_run.processed_count,
          insertedCount: summary.latest_ingest_run.inserted_count,
          skippedCount: summary.latest_ingest_run.skipped_count,
          errorCount: summary.latest_ingest_run.error_count,
        }
      : undefined,
    sourceHealth: summary.source_health,
  }
}
