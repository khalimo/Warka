export interface Source {
  id: string
  name: string
  url: string
  category: string
  description: string
  language?: string
  country?: string
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
  title: string
  excerpt: string
  content?: string
  summary?: string
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
}

export interface HomePageData {
  heroStory: Story
  secondaryStories: Story[]
  comparePreview: CompareCluster | null
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
  stories: BackendStory[]
  sources: BackendSource[]
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
  latest_stories: BackendStory[]
  somalia_stories: BackendStory[]
  world_stories: BackendStory[]
}
