import {
  AIReviewUpdatePayload,
  AIReviewUpdateResponse,
  BackendAIReviewUpdatePayload,
  BackendAIReviewUpdateResponse,
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
import {
  mapAIReviewUpdateResponse,
  mapCluster,
  mapHomePageData,
  mapPaginatedClusters,
  mapPaginatedStories,
  mapSource,
  mapStory,
} from './mappers'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || ''

class ApiClient {
  private async fetchJSON<T>(endpoint: string): Promise<T | null> {
    if (!API_BASE_URL) {
      console.warn(`No NEXT_PUBLIC_API_BASE_URL configured for ${endpoint}`)
      return null
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        cache: 'no-store',
        headers: {
          Accept: 'application/json',
        },
      })
      if (!response.ok) {
        return null
      }
      return (await response.json()) as T
    } catch (error) {
      console.error(`Failed to fetch ${endpoint}:`, error)
      return null
    }
  }

  async getHomePage(): Promise<HomePageData | null> {
    const result = await this.fetchJSON<BackendHomePageData>('/api/home')
    return result ? mapHomePageData(result) : null
  }

  async getLatestStories(limit = 20, offset = 0): Promise<PaginatedResponse<Story> | null> {
    const result = await this.fetchJSON<PaginatedResponse<BackendStory>>(
      `/api/stories/latest?limit=${limit}&offset=${offset}`
    )
    return result ? mapPaginatedStories(result) : null
  }

  async getSomaliaStories(limit = 10, offset = 0): Promise<PaginatedResponse<Story> | null> {
    const result = await this.fetchJSON<PaginatedResponse<BackendStory>>(
      `/api/stories/section/somalia?limit=${limit}&offset=${offset}`
    )
    return result ? mapPaginatedStories(result) : null
  }

  async getWorldStories(limit = 10, offset = 0): Promise<PaginatedResponse<Story> | null> {
    const result = await this.fetchJSON<PaginatedResponse<BackendStory>>(
      `/api/stories/section/world?limit=${limit}&offset=${offset}`
    )
    return result ? mapPaginatedStories(result) : null
  }

  async getStory(slug: string): Promise<Story | null> {
    const result = await this.fetchJSON<BackendStory>(`/api/stories/${slug}`)
    return result ? mapStory(result) : null
  }

  async getCompareClusters(
    limit = 10,
    offset = 0,
    hasAISynthesis?: boolean
  ): Promise<PaginatedResponse<CompareCluster> | null> {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    })
    if (typeof hasAISynthesis === 'boolean') {
      params.set('has_ai_synthesis', String(hasAISynthesis))
    }
    const result = await this.fetchJSON<PaginatedResponse<BackendCluster>>(
      `/api/clusters?${params.toString()}`
    )
    return result ? mapPaginatedClusters(result) : null
  }

  async getSources(): Promise<Source[] | null> {
    const result = await this.fetchJSON<BackendSource[]>('/api/sources')
    return result ? result.map(mapSource) : null
  }

  async checkHealth(): Promise<boolean> {
    const result = await this.fetchJSON<{ status: string }>('/api/health')
    return result?.status === 'healthy' || result?.status === 'ok'
  }

  async triggerIngestion(): Promise<{ id?: string; status?: string } | null> {
    if (!API_BASE_URL) {
      return null
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/ingest`, {
        method: 'POST',
        headers: {
          Accept: 'application/json',
        },
      })
      if (!response.ok) {
        return null
      }
      return (await response.json()) as { id?: string; status?: string }
    } catch (error) {
      console.error('Ingestion failed:', error)
      return null
    }
  }

  async updateClusterAIReview(
    clusterId: string,
    payload: AIReviewUpdatePayload
  ): Promise<AIReviewUpdateResponse | null> {
    if (!API_BASE_URL) {
      return null
    }
    const body: BackendAIReviewUpdatePayload = {
      review_status: payload.reviewStatus,
      review_note: payload.reviewNote,
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/internal/clusters/${clusterId}/ai-review`, {
        method: 'PATCH',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })
      if (!response.ok) {
        return null
      }
      const result = (await response.json()) as BackendAIReviewUpdateResponse
      return mapAIReviewUpdateResponse(result)
    } catch (error) {
      console.error('Updating AI review failed:', error)
      return null
    }
  }
}

export const apiClient = new ApiClient()
