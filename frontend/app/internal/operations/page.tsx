import { notFound } from 'next/navigation'

import { EmptyState } from '@/components/ui/EmptyState'

export const metadata = {
  title: 'Internal Operations',
  description: 'Internal health and ingestion readiness dashboard for Warka.',
}

export const dynamic = 'force-dynamic'

export default async function InternalOperationsPage() {
  if (process.env.ENABLE_INTERNAL_OPERATIONS !== 'true') {
    notFound()
  }

  return (
    <div className="container-custom py-12">
      <EmptyState
        title="Operations disabled in the public frontend"
        message="The backend operations API is now protected by an internal API key. Re-enable this view only after adding proper server-side admin authentication."
      />
    </div>
  )
}
