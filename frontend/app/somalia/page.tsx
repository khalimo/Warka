import { StoryCollectionPageClient } from '@/components/pages/StoryCollectionPageClient'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Somalia',
  description: 'Essential reporting from across Somalia, gathered in one place.',
}

export const dynamic = 'force-dynamic'

export default async function SomaliaPage() {
  const result = await apiClient.getSomaliaStories(30, 0)

  return <StoryCollectionPageClient variant="somalia" stories={result?.items || []} />
}
