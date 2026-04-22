import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { StoryCardCompact } from '@/components/story/StoryCardCompact'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Latest Stories',
  description: 'The latest reporting from Warka across Somalia and the wider world.',
}

export const dynamic = 'force-dynamic'

export default async function LatestPage() {
  const result = await apiClient.getLatestStories(50, 0)

  if (!result) {
    return (
      <div className="container-custom py-16 md:py-20">
        <LoadingSkeleton variant="list" count={6} />
        <div className="mt-8">
          <EmptyState
            title="We couldn&apos;t load the latest stories"
            message="The latest feed is temporarily unavailable. Please try again shortly."
          />
        </div>
      </div>
    )
  }

  if (result.items.length === 0) {
    return (
      <div className="container-custom py-16 md:py-20">
        <EmptyState title="No stories yet" message="Ingestion may still be running." />
      </div>
    )
  }

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <section className="border-b news-divider">
        <div className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
          <div className="mx-auto max-w-4xl">
            <SectionHeader
              title="Latest Stories"
              subtitle="The newest reporting from Warka&apos;s source network, arranged in a calm rolling feed."
            />
          </div>
        </div>
      </section>

      <section className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
        <div className="mx-auto max-w-5xl">
          <div className="section-surface divide-y divide-[#dfd4c3] overflow-hidden dark:divide-white/10">
            {result.items.map((story) => (
              <StoryCardCompact key={story.id} story={story} />
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
