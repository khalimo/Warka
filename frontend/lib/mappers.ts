import {
  BackendCluster,
  BackendHomePageData,
  BackendSource,
  BackendStory,
  CompareCluster,
  HomePageData,
  PaginatedResponse,
  Source,
  Story,
} from './types'

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

export function mapSource(source: BackendSource): Source {
  return {
    id: source.id,
    name: source.name,
    url: source.base_url || source.feed_url || '',
    category: source.category,
    description: source.description,
    language: source.language || undefined,
    country: source.country || undefined,
  }
}

export function mapStory(story: BackendStory): Story {
  return {
    id: story.id,
    slug: story.slug,
    title: story.title,
    excerpt: story.excerpt || story.summary || '',
    content: story.content_html || undefined,
    summary: story.summary || undefined,
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
    createdAt: cluster.created_at || undefined,
    updatedAt: cluster.updated_at || undefined,
    storyCount: cluster.story_count || undefined,
    stories: cluster.stories.map(mapStory),
    sources: cluster.sources.map(mapSource),
  }
}

export function mapHomePageData(home: BackendHomePageData): HomePageData {
  return {
    heroStory: mapStory(home.hero_story),
    secondaryStories: home.secondary_stories.map(mapStory),
    comparePreview: home.compare_preview ? mapCluster(home.compare_preview) : null,
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
