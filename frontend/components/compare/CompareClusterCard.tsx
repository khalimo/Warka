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
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md">
      <div className="p-6">
        <div className="eyebrow mb-2">Compare Coverage</div>
        <h3 className="text-xl font-bold text-gray-900">{cluster.title}</h3>

        <div className="mt-4 space-y-4">
          <div className="rounded-lg bg-green-50 p-4">
            <h4 className="mb-1 font-semibold text-green-900">What sources agree on</h4>
            <p className="text-sm text-green-800">{cluster.commonFacts || cluster.neutralSummary}</p>
          </div>

          <div>
            <h4 className="mb-1 font-semibold text-gray-900">Where coverage differs</h4>
            <p className="text-sm text-gray-700">
              {cluster.coverageDifferences || 'This story is still developing across sources.'}
            </p>
          </div>

          <div>
            <h4 className="mb-2 font-semibold text-gray-900">Sources</h4>
            <div className="flex flex-wrap gap-2">
              {cluster.sources.map((source) => (
                <SourceBadge key={source.id} source={source} size="sm" />
              ))}
            </div>
          </div>

          <button
            onClick={() => setExpanded((value) => !value)}
            className="flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            {expanded ? 'Hide stories' : `View ${cluster.stories.length} stories`}
          </button>

          {expanded ? (
            <div className="space-y-3 border-t border-gray-100 pt-4">
              {cluster.stories.map((story) => (
                <Link key={story.id} href={`/story/${story.slug}`} className="block rounded-lg p-3 hover:bg-gray-50">
                  <h5 className="font-medium text-gray-900">{story.title}</h5>
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
