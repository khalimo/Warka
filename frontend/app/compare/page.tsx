import { ComparePageClient } from '@/components/pages/ComparePageClient'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Compare Coverage',
  description: 'See how different outlets cover the same story and where their reporting differs.',
}

export const dynamic = 'force-dynamic'

export default async function ComparePage() {
  const result = await apiClient.getCompareClusters(20, 0)

  return <ComparePageClient clusters={result?.items || []} />
}
