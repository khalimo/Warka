import { SourcesPageClient } from '@/components/pages/SourcesPageClient'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Sources',
  description: 'Active sources monitored by Warka with language and coverage transparency.',
}

export const dynamic = 'force-dynamic'

export default async function SourcesPage() {
  const sources = await apiClient.getSources()

  return <SourcesPageClient sources={sources || []} />
}
