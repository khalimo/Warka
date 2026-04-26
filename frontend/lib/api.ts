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
import {
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
    hasAISynthesis?: boolean,
    aiReviewStatus?: string,
    renderableOnly = true,
    filter?: string
  ): Promise<PaginatedResponse<CompareCluster> | null> {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
      renderable_only: String(renderableOnly),
    })
    if (typeof hasAISynthesis === 'boolean') {
      params.set('has_ai_synthesis', String(hasAISynthesis))
    }
    if (aiReviewStatus) {
      params.set('ai_review_status', aiReviewStatus)
    }
    if (filter && filter !== 'all') {
      if (filter === 'somalia' || filter === 'world') {
        params.set('region', filter)
      } else {
        params.set('category', filter)
      }
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
}

export const apiClient = new ApiClient()
