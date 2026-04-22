import { CompareClusterCard } from '@/components/compare/CompareClusterCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Compare Coverage',
  description: 'See how different outlets cover the same story and where their reporting differs.',
}

export const dynamic = 'force-dynamic'

export default async function ComparePage() {
  const result = await apiClient.getCompareClusters(20, 0)

  if (!result || result.items.length === 0) {
    return (
      <div className="container-custom py-16 md:py-20">
        <EmptyState
          title="No comparisons yet"
          message="Clusters will appear here once stories are ingested and grouped."
        />
      </div>
    )
  }

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <section className="border-b news-divider">
        <div className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
          <div className="mx-auto max-w-5xl">
            <div className="mb-5 flex justify-center sm:mb-6">
              <span className="signature-chip">Compare Coverage</span>
            </div>
            <SectionHeader
              title="Compare Coverage"
              subtitle="See how different outlets cover the same story, what they agree on, and where their emphasis shifts."
              centered
            />
          </div>
        </div>
      </section>

      <section className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
        <div className="mx-auto max-w-5xl space-y-6 sm:space-y-8 md:space-y-10">
          {result.items.map((cluster) => (
            <CompareClusterCard key={cluster.id} cluster={cluster} />
          ))}
        </div>
      </section>
    </div>
  )
}
