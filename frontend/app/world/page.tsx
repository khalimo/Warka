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
      <div className="container-custom py-16 md:py-20">
        <EmptyState title="No world stories yet" message="Check back soon." />
      </div>
    )
  }

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <section className="border-b news-divider">
        <div className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
          <div className="mx-auto max-w-4xl">
            <SectionHeader
              title="World"
              subtitle="Global reporting that helps Somali readers keep the wider picture in view."
            />
          </div>
        </div>
      </section>

      <section className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
        <div className="grid grid-cols-1 gap-5 sm:gap-6 md:grid-cols-2 xl:grid-cols-3 xl:gap-8">
          {result.items.map((story) => (
            <StoryCardLarge key={story.id} story={story} />
          ))}
        </div>
      </section>
    </div>
  )
}
