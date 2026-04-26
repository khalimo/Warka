'use client'

import { CompareClusterCard } from '@/components/compare/CompareClusterCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { useLanguage } from '@/components/language/LanguageProvider'
import { CompareCluster } from '@/lib/types'

export function ComparePageClient({
  clusters,
  activeSourceCount = 0,
  readyStoryCount = 0,
}: {
  clusters: CompareCluster[]
  activeSourceCount?: number
  readyStoryCount?: number
}) {
  const { dictionary } = useLanguage()

  if (clusters.length === 0) {
    return (
      <div className="bg-paper dark:bg-[#141b1d]">
        <section className="container-custom py-16 md:py-20">
          <div className="mx-auto max-w-4xl">
            <div className="mb-8">
              <EmptyState
                title={dictionary.compare.watchTitle}
                message={dictionary.compare.watchMessage}
              />
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                [dictionary.compare.activeSources, activeSourceCount],
                [dictionary.compare.scannedStories, readyStoryCount],
                [dictionary.compare.waitingTopics, Math.max(0, readyStoryCount - clusters.length)],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-editorial border border-[#ded2c0] bg-white/80 px-4 py-4 text-center dark:border-white/10 dark:bg-[#182124]"
                >
                  <div className="font-serif text-3xl font-bold text-ink dark:text-[#fbf7f0]">{value}</div>
                  <div className="mt-1 text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-ink/48 dark:text-[#b7b1a8]">
                    {label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
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
