import Link from 'next/link'
import { CompareCluster } from '@/lib/types'
import { SourceBadge } from '@/components/story/SourceBadge'

export function ComparePreviewCard({ cluster }: { cluster: CompareCluster }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-gradient-to-br from-gray-50 to-white p-6">
      <h3 className="text-lg font-bold">{cluster.title}</h3>
      <p className="mt-2 line-clamp-2 text-sm text-gray-600">{cluster.commonFacts}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {cluster.sources.slice(0, 3).map((source) => (
          <SourceBadge key={source.id} source={source} size="sm" />
        ))}
      </div>
      <Link href="/compare" className="mt-4 inline-block text-sm font-medium text-primary-600 hover:underline">
        Compare perspectives →
      </Link>
    </div>
  )
}
