import { CompareClusterCard } from '@/components/compare/CompareClusterCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Compare Coverage',
  description: 'See how different outlets cover the same story and where their reporting differs.',
}

export default async function ComparePage() {
  const result = await apiClient.getCompareClusters(20, 0)

  if (!result || result.items.length === 0) {
    return (
      <div className="container-custom py-12">
        <EmptyState
          title="No comparisons yet"
          message="Clusters will appear here once stories are ingested and grouped."
        />
      </div>
    )
  }

  return (
    <div className="container-custom py-12">
      <div className="mx-auto max-w-4xl">
        <SectionHeader
          title="Compare Coverage"
          subtitle="See how different outlets cover the same story, what they agree on, and where their emphasis shifts."
          centered
        />
        <div className="space-y-8">
          {result.items.map((cluster) => (
            <CompareClusterCard key={cluster.id} cluster={cluster} />
          ))}
        </div>
      </div>
    </div>
  )
}
