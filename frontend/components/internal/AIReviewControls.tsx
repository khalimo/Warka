'use client'

import { useMemo, useState } from 'react'

import { AIReviewUpdatePayload, CompareCluster } from '@/lib/types'

const REVIEW_STATES: AIReviewUpdatePayload['reviewStatus'][] = [
  'unreviewed',
  'good',
  'weak',
  'misleading',
  'hallucinated',
]

type Props = {
  cluster: CompareCluster
}

export function AIReviewControls({ cluster }: Props) {
  const [reviewStatus, setReviewStatus] = useState<AIReviewUpdatePayload['reviewStatus']>(
    cluster.aiReviewStatus || 'unreviewed'
  )
  const [savedStatus, setSavedStatus] = useState<AIReviewUpdatePayload['reviewStatus']>(
    cluster.aiReviewStatus || 'unreviewed'
  )
  const [reviewNote, setReviewNote] = useState(cluster.aiReviewNote || '')

  const remaining = useMemo(() => 500 - reviewNote.length, [reviewNote.length])

  return (
    <section className="border-t border-gray-200 bg-white px-6 py-5">
      <div className="grid gap-5 lg:grid-cols-[1fr_1.2fr_auto] lg:items-end">
        <div className="space-y-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-wide text-gray-500">Review status</div>
            <div className="mt-2 flex flex-wrap gap-2">
              {REVIEW_STATES.map((option) => {
                const active = option === reviewStatus
                return (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setReviewStatus(option)}
                    className={`rounded-full border px-3 py-1.5 text-sm font-medium transition ${
                      active
                        ? 'border-gray-900 bg-gray-900 text-white'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                    }`}
                  >
                    {option}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="text-sm text-gray-600">
            Current saved state: <span className="font-medium text-gray-900">{savedStatus}</span>
          </div>
        </div>

        <div>
          <label htmlFor={`review-note-${cluster.id}`} className="text-sm font-medium text-gray-900">
            Reviewer note
          </label>
          <textarea
            id={`review-note-${cluster.id}`}
            value={reviewNote}
            onChange={(event) => setReviewNote(event.target.value.slice(0, 500))}
            rows={4}
            maxLength={500}
            placeholder="Optional note about whether the AI summary is trustworthy, weak, or misleading."
            className="mt-2 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none transition focus:border-gray-500"
          />
          <div className="mt-1 text-right text-xs text-gray-500">{remaining} characters remaining</div>
        </div>

        <div className="space-y-3">
          <button
            type="button"
            disabled
            className="w-full rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-400"
          >
            Saving disabled
          </button>

          <div className="min-h-[2.5rem] text-sm">
            <div className="text-gray-600">
              Admin writes are disabled in the public frontend until proper authentication is added.
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
