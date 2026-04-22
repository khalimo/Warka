import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { StoryCardLarge } from '@/components/story/StoryCardLarge'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'World',
  description: 'Global reporting that matters to Somali readers.',
}

export const dynamic = 'force-dynamic'

export default async function WorldPage() {
  const result = await apiClient.getWorldStories(30, 0)

  if (!result || result.items.length === 0) {
    return (
      <div className="container-custom py-12">
        <EmptyState title="No world stories yet" message="Check back soon." />
      </div>
    )
  }

  return (
    <div className="container-custom py-12">
      <SectionHeader
        title="World"
        subtitle="Global reporting that helps Somali readers keep the wider picture in view."
      />
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {result.items.map((story) => (
          <StoryCardLarge key={story.id} story={story} />
        ))}
      </div>
    </div>
  )
}
