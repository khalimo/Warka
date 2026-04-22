import { notFound } from 'next/navigation'

import { AIReviewControls } from '@/components/internal/AIReviewControls'
import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { TimeAgo } from '@/components/ui/TimeAgo'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Internal AI Review',
  description: 'Internal QA view for comparing deterministic and AI cluster synthesis.',
}

export const dynamic = 'force-dynamic'

type PageProps = {
  searchParams?: {
    limit?: string
    status?: string
  }
}

const REVIEW_FILTERS = ['all', 'unreviewed', 'good', 'weak', 'misleading', 'hallucinated'] as const

function normalizeStatus(rawStatus?: string): (typeof REVIEW_FILTERS)[number] {
  const normalized = (rawStatus || '').trim().toLowerCase()
  if (REVIEW_FILTERS.includes(normalized as (typeof REVIEW_FILTERS)[number])) {
    return normalized as (typeof REVIEW_FILTERS)[number]
  }
  return 'unreviewed'
}

function normalizeLimit(rawLimit?: string): number {
  var parsed = Number(rawLimit)
  if (!parsed || parsed < 1) {
    return 10
  }
  if (parsed > 50) {
    return 50
  }
  if (parsed <= 10) {
    return 10
  }
  if (parsed <= 20) {
    return 20
  }
  return 50
}

function formatThemes(themes?: string[]): string {
  if (!themes || themes.length === 0) {
    return 'None'
  }
  return themes.join(', ')
}

function renderTextBlock(value?: string): string {
  if (!value || !value.trim()) {
    return 'Not available'
  }
  return value
}

export default async function InternalAIReviewPage({ searchParams }: PageProps) {
  if (process.env.ENABLE_INTERNAL_AI_REVIEW !== 'true') {
    notFound()
  }

  const limit = normalizeLimit(searchParams?.limit)
  const statusFilter = normalizeStatus(searchParams?.status)
  const result = await apiClient.getCompareClusters(
    limit,
    0,
    true,
    statusFilter === 'all' ? undefined : statusFilter
  )

  return (
    <div className="container-custom py-12">
      <div className="mx-auto max-w-6xl space-y-8">
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          Internal QA / beta review only. This page compares deterministic cluster output with optional AI synthesis.
        </div>

        <SectionHeader
          title="AI Cluster Review"
          subtitle="Manual side-by-side review for the newest AI-enriched clusters."
        />

        <div className="flex flex-wrap gap-3">
          {[10, 20, 50].map((option) => {
            const isActive = option === limit
            return (
              <a
                key={option}
                href={`/internal/ai-review?limit=${option}&status=${statusFilter}`}
                className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
                  isActive
                    ? 'border-gray-900 bg-gray-900 text-white'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                Show {option}
              </a>
            )
          })}
        </div>

        <div className="flex flex-wrap gap-3">
          {REVIEW_FILTERS.map((option) => {
            const isActive = option === statusFilter
            return (
              <a
                key={option}
                href={`/internal/ai-review?limit=${limit}&status=${option}`}
                className={`rounded-full border px-4 py-2 text-sm font-medium capitalize transition ${
                  isActive
                    ? 'border-blue-700 bg-blue-700 text-white'
                    : 'border-blue-200 bg-blue-50 text-blue-800 hover:border-blue-300'
                }`}
              >
                {option}
              </a>
            )
          })}
        </div>

        {!result || result.items.length === 0 ? (
          <EmptyState
            title="No AI-reviewed clusters found"
            message="Run the AI synthesis CLI first, then come back here for side-by-side review."
          />
        ) : (
          <div className="space-y-8">
            {result.items.map((cluster) => (
              <article key={cluster.id} className="overflow-hidden rounded-xl border border-gray-200 bg-white">
                <div className="border-b border-gray-200 bg-gray-50 px-6 py-5">
                  <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div className="space-y-2">
                      <div className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Cluster ID: {cluster.id}
                      </div>
                      <h2 className="text-2xl font-serif font-bold text-gray-900">{cluster.title}</h2>
                      <div className="flex flex-wrap gap-2 text-sm text-gray-600">
                        <span>Stories: {cluster.storyCount ?? cluster.stories.length}</span>
                        <span>Sources: {cluster.sources.map((source) => source.name).join(', ') || 'Unknown'}</span>
                      </div>
                    </div>

                    <div className="grid gap-2 text-sm text-gray-600">
                      <div>
                        Created:{' '}
                        {cluster.createdAt ? <TimeAgo date={cluster.createdAt} /> : 'Unknown'}
                      </div>
                      <div>
                        Updated:{' '}
                        {cluster.updatedAt ? <TimeAgo date={cluster.updatedAt} /> : 'Unknown'}
                      </div>
                      <div>
                        AI generated:{' '}
                        {cluster.aiGeneratedAt ? <TimeAgo date={cluster.aiGeneratedAt} /> : 'Not recorded'}
                      </div>
                      <div>AI model: {cluster.aiModelUsed || 'Not recorded'}</div>
                      <div>Review status: {cluster.aiReviewStatus || 'unreviewed'}</div>
                    </div>
                  </div>
                </div>

                <div className="grid gap-6 p-6 lg:grid-cols-2">
                  <section className="space-y-4 rounded-lg border border-gray-200 bg-gray-50 p-5">
                    <div>
                      <div className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                        Deterministic
                      </div>
                      <h3 className="mt-1 text-lg font-semibold text-gray-900">Current compare output</h3>
                    </div>

                    <div>
                      <div className="text-sm font-medium text-gray-900">Neutral summary</div>
                      <p className="mt-1 text-sm leading-6 text-gray-700">{renderTextBlock(cluster.neutralSummary)}</p>
                    </div>

                    <div>
                      <div className="text-sm font-medium text-gray-900">Coverage differences</div>
                      <p className="mt-1 text-sm leading-6 text-gray-700">
                        {renderTextBlock(cluster.coverageDifferences)}
                      </p>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-2">
                      <div>
                        <div className="text-sm font-medium text-gray-900">Consensus level</div>
                        <p className="mt-1 text-sm text-gray-700">{cluster.consensusLevel || 'Not available'}</p>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">Key themes</div>
                        <p className="mt-1 text-sm text-gray-700">{formatThemes(cluster.keyThemes)}</p>
                      </div>
                    </div>
                  </section>

                  <section className="space-y-4 rounded-lg border border-blue-200 bg-blue-50 p-5">
                    <div>
                      <div className="text-xs font-semibold uppercase tracking-wide text-blue-700">
                        AI synthesis
                      </div>
                      <h3 className="mt-1 text-lg font-semibold text-gray-900">Review-only generated output</h3>
                    </div>

                    <div>
                      <div className="text-sm font-medium text-gray-900">Neutral summary</div>
                      <p className="mt-1 text-sm leading-6 text-gray-700">
                        {renderTextBlock(cluster.aiNeutralSummary)}
                      </p>
                    </div>

                    <div>
                      <div className="text-sm font-medium text-gray-900">Coverage differences</div>
                      <p className="mt-1 text-sm leading-6 text-gray-700">
                        {renderTextBlock(cluster.aiCoverageDifferences)}
                      </p>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-2">
                      <div>
                        <div className="text-sm font-medium text-gray-900">Consensus level</div>
                        <p className="mt-1 text-sm text-gray-700">{cluster.aiConsensusLevel || 'Not available'}</p>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">Key themes</div>
                        <p className="mt-1 text-sm text-gray-700">{formatThemes(cluster.aiKeyThemes)}</p>
                      </div>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-2">
                      <div>
                        <div className="text-sm font-medium text-gray-900">AI model</div>
                        <p className="mt-1 text-sm text-gray-700">{cluster.aiModelUsed || 'Not recorded'}</p>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">Has AI synthesis</div>
                        <p className="mt-1 text-sm text-gray-700">{cluster.hasAISynthesis ? 'Yes' : 'No'}</p>
                      </div>
                    </div>
                  </section>
                </div>

                <AIReviewControls cluster={cluster} />
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
