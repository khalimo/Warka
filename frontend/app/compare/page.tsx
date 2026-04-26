import { ComparePageClient } from '@/components/pages/ComparePageClient'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Compare Coverage',
  description: 'See how different outlets cover the same story and where their reporting differs.',
}

export const dynamic = 'force-dynamic'

export default async function ComparePage() {
  const [result, sources, latest] = await Promise.all([
    apiClient.getCompareClusters(20, 0),
    apiClient.getSources(),
    apiClient.getLatestStories(12, 0),
  ])

  return (
    <ComparePageClient
      clusters={result?.items || []}
      activeSourceCount={sources?.length || 0}
      readyStoryCount={latest?.total || latest?.items.length || 0}
    />
  )
}
