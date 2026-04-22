'use client'

import { CompareClusterCard } from '@/components/compare/CompareClusterCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { useLanguage } from '@/components/language/LanguageProvider'
import { CompareCluster } from '@/lib/types'

export function ComparePageClient({ clusters }: { clusters: CompareCluster[] }) {
  const { dictionary } = useLanguage()

  if (clusters.length === 0) {
    return (
      <div className="container-custom py-16 md:py-20">
        <EmptyState
          title={dictionary.pages.compare.emptyTitle}
          message={dictionary.pages.compare.emptyMessage}
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
              <span className="signature-chip">{dictionary.sections.compareCoverage}</span>
            </div>
            <SectionHeader
              title={dictionary.pages.compare.title}
              subtitle={dictionary.pages.compare.subtitle}
              centered
            />
          </div>
        </div>
      </section>

      <section className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
        <div className="mx-auto max-w-5xl space-y-6 sm:space-y-8 md:space-y-10">
          {clusters.map((cluster) => (
            <CompareClusterCard key={cluster.id} cluster={cluster} />
          ))}
        </div>
      </section>
    </div>
  )
}
