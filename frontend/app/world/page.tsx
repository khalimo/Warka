import { StoryCollectionPageClient } from '@/components/pages/StoryCollectionPageClient'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'World',
  description: 'Global reporting that matters to Somali readers.',
}

export const dynamic = 'force-dynamic'

export default async function WorldPage() {
  const result = await apiClient.getWorldStories(30, 0)

  return <StoryCollectionPageClient variant="world" stories={result?.items || []} />
}
