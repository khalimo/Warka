'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { CompareCluster } from '@/lib/types'
import { SourceBadge } from '@/components/story/SourceBadge'

interface CompareClusterCardProps {
  cluster: CompareCluster
}

export function CompareClusterCard({ cluster }: CompareClusterCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="overflow-hidden rounded-editorial border border-[#dccfbe] bg-white/92 shadow-lift transition duration-300 ease-editorial hover:shadow-editorial dark:border-white/10 dark:bg-[#182124]">
      <div className="p-5 sm:p-6 md:p-7">
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <span className="signature-chip">Compare Coverage</span>
          <span className="text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-ink/45 dark:text-[#b7b1a8]">
            Signature report
          </span>
        </div>
        <h3 className="text-[1.45rem] font-bold leading-tight text-ink dark:text-[#fbf7f0] sm:text-2xl">{cluster.title}</h3>

        <div className="mt-5 space-y-4 sm:mt-6 sm:space-y-5">
          <div className="rounded-editorial border border-acacia/25 bg-acacia/10 p-4 dark:border-acacia/20 dark:bg-acacia/10">
            <h4 className="mb-2 text-sm font-semibold uppercase tracking-[0.14em] text-acacia">What sources agree on</h4>
            <p className="text-sm leading-7 text-ink/78 dark:text-[#e2ddd5]">{cluster.commonFacts || cluster.neutralSummary}</p>
          </div>

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_15rem] lg:items-start">
            <div>
              <h4 className="mb-2 text-sm font-semibold uppercase tracking-[0.14em] text-ink/60 dark:text-[#bbb4ab]">Where coverage differs</h4>
              <p className="text-sm leading-7 text-ink/74 dark:text-[#d9d3ca]">
                {cluster.coverageDifferences || 'This story is still developing across sources.'}
              </p>
            </div>

            <div>
              <h4 className="mb-2 text-sm font-semibold uppercase tracking-[0.14em] text-ink/60 dark:text-[#bbb4ab]">Sources</h4>
              <div className="flex flex-wrap gap-2">
                {cluster.sources.map((source) => (
                  <SourceBadge key={source.id} source={source} size="sm" />
                ))}
              </div>
            </div>
          </div>

          <button
            onClick={() => setExpanded((value) => !value)}
            className="inline-flex min-h-[44px] items-center gap-2 text-sm font-semibold uppercase tracking-[0.14em] text-primary-600 transition-colors duration-300 ease-editorial hover:text-primary-700 dark:text-primary-200 dark:hover:text-primary-100"
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            {expanded ? 'Hide stories' : `View ${cluster.stories.length} stories`}
          </button>

          {expanded ? (
            <div className="space-y-3 border-t news-divider pt-5">
              {cluster.stories.map((story) => (
                <Link
                  key={story.id}
                  href={`/story/${story.slug}`}
                  className="block rounded-editorial border border-transparent p-3 transition-colors duration-300 ease-editorial hover:border-[#d9ccba] hover:bg-paper dark:hover:border-white/10 dark:hover:bg-[#1d2629]"
                >
                  <h5 className="font-serif text-lg font-bold text-ink dark:text-[#fbf7f0]">{story.title}</h5>
                  <div className="mt-2">
                    <SourceBadge source={story.source} size="sm" />
                  </div>
                </Link>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
