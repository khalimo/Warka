import { ComparePageClient } from '@/components/pages/ComparePageClient'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Compare Coverage',
  description: 'See how different outlets cover the same story and where their reporting differs.',
}

export const dynamic = 'force-dynamic'

type PageProps = {
  searchParams?: {
    page?: string
  }
}

function normalizePage(rawPage?: string): number {
  const parsed = Number(rawPage)
  if (!Number.isFinite(parsed) || parsed < 1) {
    return 1
  }
  return Math.floor(parsed)
}

export default async function ComparePage({ searchParams }: PageProps) {
  const page = normalizePage(searchParams?.page)
  const limit = 20
  const offset = (page - 1) * limit
  const [result, sources, latest] = await Promise.all([
    apiClient.getCompareClusters(limit, offset, undefined, undefined, true),
    apiClient.getSources(),
    apiClient.getLatestStories(12, 0),
  ])

  return (
    <ComparePageClient
      clusters={result?.items || []}
      total={result?.total || 0}
      limit={result?.limit || limit}
      offset={result?.offset || offset}
      activeSourceCount={sources?.length || 0}
      readyStoryCount={latest?.total || latest?.items.length || 0}
      apiUnavailable={!result}
    />
  )
}
