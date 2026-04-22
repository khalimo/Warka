import { StoryCollectionPageClient } from '@/components/pages/StoryCollectionPageClient'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Latest Stories',
  description: 'The latest reporting from Warka across Somalia and the wider world.',
}

export const dynamic = 'force-dynamic'

export default async function LatestPage() {
  const result = await apiClient.getLatestStories(50, 0)

  return <StoryCollectionPageClient variant="latest" stories={result?.items || []} failed={!result} />
}
