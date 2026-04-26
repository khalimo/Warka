import { notFound } from 'next/navigation'

import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { TimeAgo } from '@/components/ui/TimeAgo'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Internal Operations',
  description: 'Internal health and ingestion readiness dashboard for Warka.',
}

export const dynamic = 'force-dynamic'

function statusTone(status?: string) {
  if (status === 'completed' || status === 'verified' || status === 'ok') {
    return 'border-emerald-200 bg-emerald-50 text-emerald-900'
  }
  if (status === 'running' || status === 'pending') {
    return 'border-amber-200 bg-amber-50 text-amber-900'
  }
  return 'border-red-200 bg-red-50 text-red-900'
}

export default async function InternalOperationsPage() {
  if (process.env.ENABLE_INTERNAL_OPERATIONS !== 'true') {
    notFound()
  }

  const summary = await apiClient.getOperationsSummary()

  if (!summary) {
    return (
      <div className="container-custom py-12">
        <EmptyState title="Operations unavailable" message="The backend operations summary could not be loaded." />
      </div>
    )
  }

  const failedSources = summary.sourceHealth.filter((source) => !source.is_enabled || source.last_error)

  return (
    <div className="container-custom py-12">
      <div className="mx-auto max-w-6xl space-y-8">
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          Internal operations view. Keep this route disabled publicly unless protected by your deployment layer.
        </div>

        <SectionHeader
          title="Operations"
          subtitle="Ingestion, source health, translation coverage sample, and clustering readiness."
        />

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          {[
            ['Stories', summary.storyCount],
            ['Clusters', summary.clusterCount],
            ['Active sources', summary.activeSourceCount],
            ['All sources', summary.sourceCount],
            ['Translated sample', summary.translatedStorySampleCount],
          ].map(([label, value]) => (
            <div key={label} className="rounded-xl border border-gray-200 bg-white p-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-gray-500">{label}</div>
              <div className="mt-2 text-3xl font-semibold text-gray-900">{value}</div>
            </div>
          ))}
        </div>

        <section className="rounded-xl border border-gray-200 bg-white p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Latest ingest run</h2>
              <p className="mt-1 text-sm text-gray-600">
                Generated <TimeAgo date={summary.generatedAt} />
              </p>
            </div>
            <span className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${statusTone(summary.latestIngestRun?.status)}`}>
              {summary.latestIngestRun?.status || 'not run'}
            </span>
          </div>

          {summary.latestIngestRun ? (
            <div className="mt-5 grid gap-3 sm:grid-cols-4">
              {[
                ['Processed', summary.latestIngestRun.processedCount],
                ['Inserted', summary.latestIngestRun.insertedCount],
                ['Skipped', summary.latestIngestRun.skippedCount],
                ['Errors', summary.latestIngestRun.errorCount],
              ].map(([label, value]) => (
                <div key={label} className="rounded-lg border border-gray-100 bg-gray-50 p-4">
                  <div className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</div>
                  <div className="mt-2 text-2xl font-semibold text-gray-900">{value}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="mt-5 text-sm text-gray-600">No ingestion run has been recorded yet.</p>
          )}
        </section>

        <section className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="text-xl font-semibold text-gray-900">Sources needing attention</h2>
          {failedSources.length === 0 ? (
            <p className="mt-3 text-sm text-gray-600">No failed or disabled sources are currently reported.</p>
          ) : (
            <div className="mt-5 divide-y divide-gray-100">
              {failedSources.slice(0, 12).map((source) => (
                <div key={source.id} className="grid gap-2 py-4 md:grid-cols-[1fr_auto] md:items-center">
                  <div>
                    <div className="font-medium text-gray-900">{source.name}</div>
                    <div className="mt-1 text-sm text-gray-600">{source.last_error || source.validation_status}</div>
                  </div>
                  <span className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${statusTone(source.validation_status || '')}`}>
                    score {source.health_score ?? 0}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
