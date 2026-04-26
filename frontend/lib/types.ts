import type { AppLanguage } from './i18n'

export interface Source {
  id: string
  name: string
  url: string
  category: string
  description: string
  language?: string
  country?: string
  isActive?: boolean
  lastSuccessAt?: string
}

export interface Framing {
  id: string
  label: string
  description: string
  tone: 'positive' | 'neutral' | 'negative' | 'mixed'
}

export interface Story {
  id: string
  slug: string
  lang: AppLanguage
  title: string
  excerpt: string
  content?: string
  summary?: string
  translations?: {
    headline?: Partial<Record<AppLanguage, string>>
    excerpt?: Partial<Record<AppLanguage, string>>
    summary?: Partial<Record<AppLanguage, string>>
    content?: Partial<Record<AppLanguage, string>>
  }
  source: Source
  publishedAt: string
  updatedAt?: string
  region: string
  category: string
  topics: string[]
  framing?: Framing
  imageUrl?: string
  originalUrl: string
  readingTime?: number
  clusterId?: string
  isBreaking: boolean
}

export interface CompareCluster {
  id: string
  title: string
  commonFacts: string
  coverageDifferences: string
  stories: Story[]
  sources: Source[]
  neutralSummary: string
  keyThemes: string[]
  consensusLevel: 'high' | 'medium' | 'low'
  aiNeutralSummary?: string
  aiCoverageDifferences?: string
  aiConsensusLevel?: 'high' | 'medium' | 'low'
  aiKeyThemes?: string[]
  aiGeneratedAt?: string
  aiModelUsed?: string
  hasAISynthesis?: boolean
  aiReviewStatus?: 'unreviewed' | 'good' | 'weak' | 'misleading' | 'hallucinated'
  aiReviewNote?: string
  aiReviewedAt?: string
  createdAt?: string
  updatedAt?: string
  storyCount?: number
  confidenceScore?: number
  eventSignature?: {
    method?: string
    confidence?: number
    components?: Record<string, number>
    entities?: string[]
    event_terms?: string[]
    source_count?: number
    languages?: string[]
    temporal_span_hours?: number
  }
}

export interface HomePageData {
  heroStory: Story
  secondaryStories: Story[]
  comparePreview: CompareCluster | null
  compareClusters: CompareCluster[]
  latestStories: Story[]
  somaliaStories: Story[]
  worldStories: Story[]
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface BackendSource {
  id: string
  name: string
  base_url?: string | null
  feed_url?: string | null
  category: string
  description: string
  language?: string | null
  country?: string | null
  is_active?: boolean
  last_success_at?: string | null
}

export interface BackendFraming {
  id: string
  label: string
  description: string
  tone: 'positive' | 'neutral' | 'negative' | 'mixed'
}

export interface BackendStory {
  id: string
  slug: string
  title: string
  excerpt?: string | null
  content_html?: string | null
  summary?: string | null
  source: BackendSource
  published_at: string
  updated_at?: string | null
  region: string
  category: string
  topics?: string[] | null
  translations?: {
    headline?: Partial<Record<AppLanguage, string>>
    excerpt?: Partial<Record<AppLanguage, string>>
    summary?: Partial<Record<AppLanguage, string>>
    content?: Partial<Record<AppLanguage, string>>
  } | null
  framing?: BackendFraming | null
  image_url?: string | null
  original_url: string
  reading_time?: number | null
  cluster_id?: string | null
  is_breaking: boolean
}

export interface BackendCluster {
  id: string
  title: string
  common_facts?: string | null
  coverage_differences?: string | null
  neutral_summary?: string | null
  key_themes?: string[] | null
  consensus_level: 'high' | 'medium' | 'low'
  ai_neutral_summary?: string | null
  ai_coverage_differences?: string | null
  ai_consensus_level?: 'high' | 'medium' | 'low' | null
  ai_key_themes?: string[] | null
  ai_generated_at?: string | null
  ai_model_used?: string | null
  has_ai_synthesis?: boolean
  ai_review_status?: 'unreviewed' | 'good' | 'weak' | 'misleading' | 'hallucinated' | null
  ai_review_note?: string | null
  ai_reviewed_at?: string | null
  created_at?: string
  updated_at?: string | null
  story_count?: number
  confidence_score?: number | null
  event_signature?: CompareCluster['eventSignature'] | null
  stories?: BackendStory[] | null
  sources?: BackendSource[] | null
}

export interface AIReviewUpdatePayload {
  reviewStatus: 'unreviewed' | 'good' | 'weak' | 'misleading' | 'hallucinated'
  reviewNote?: string
}

export interface BackendAIReviewUpdatePayload {
  review_status: 'unreviewed' | 'good' | 'weak' | 'misleading' | 'hallucinated'
  review_note?: string
}

export interface AIReviewUpdateResponse {
  clusterId: string
  aiReviewStatus: 'unreviewed' | 'good' | 'weak' | 'misleading' | 'hallucinated'
  aiReviewNote?: string
  aiReviewedAt?: string
}

export interface BackendAIReviewUpdateResponse {
  cluster_id: string
  ai_review_status: 'unreviewed' | 'good' | 'weak' | 'misleading' | 'hallucinated'
  ai_review_note?: string | null
  ai_reviewed_at?: string | null
}

export interface BackendHomePageData {
  hero_story: BackendStory
  secondary_stories: BackendStory[]
  compare_preview: BackendCluster | null
  compare_clusters?: BackendCluster[] | null
  latest_stories: BackendStory[]
  somalia_stories: BackendStory[]
  world_stories: BackendStory[]
}

export interface BackendIngestRun {
  id: string
  started_at: string
  completed_at?: string | null
  status: string
  processed_count: number
  inserted_count: number
  updated_count: number
  skipped_count: number
  error_count: number
  details_json?: Record<string, unknown>
}

export interface BackendOperationsSummary {
  status: string
  generated_at: string
  story_count: number
  cluster_count: number
  source_count: number
  active_source_count: number
  translated_story_sample_count: number
  latest_ingest_run?: BackendIngestRun | null
  source_health: Array<{
    id: string
    name: string
    is_enabled: boolean
    category?: string | null
    language?: string | null
    validation_status?: string | null
    stories_ingested_24h?: number
    health_score?: number
    last_error?: string | null
  }>
}

export interface OperationsSummary {
  status: string
  generatedAt: string
  storyCount: number
  clusterCount: number
  sourceCount: number
  activeSourceCount: number
  translatedStorySampleCount: number
  latestIngestRun?: {
    id: string
    startedAt: string
    completedAt?: string
    status: string
    processedCount: number
    insertedCount: number
    skippedCount: number
    errorCount: number
  }
  sourceHealth: BackendOperationsSummary['source_health']
}
