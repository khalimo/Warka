import { CompareClusterCard } from '@/components/compare/CompareClusterCard'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { EmptyState } from '@/components/ui/EmptyState'
import { HeroStoryCard } from '@/components/story/HeroStoryCard'
import { StoryCardCompact } from '@/components/story/StoryCardCompact'
import { StoryCardLarge } from '@/components/story/StoryCardLarge'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Independent Somali News',
  description: 'Independent Somali news with source transparency and multi-source coverage comparison.',
}

export default async function HomePage() {
  const homeData = await apiClient.getHomePage()

  if (!homeData) {
    return (
      <div className="container-custom py-20 text-center">
        <h1 className="mb-4 text-3xl font-bold">Welcome to Warka</h1>
        <p className="text-gray-600">Loading the latest news from Somalia...</p>
      </div>
    )
  }

  return (
    <div className="bg-white">
      <section className="border-b border-gray-200">
        <div className="container-custom py-8 md:py-12">
          <HeroStoryCard story={homeData.heroStory} />
        </div>
      </section>

      <section className="container-custom py-12">
        <SectionHeader
          title="Top Stories"
          subtitle="The biggest developments shaping Somalia and the wider region."
        />
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {homeData.secondaryStories.map((story) => (
            <StoryCardLarge key={story.id} story={story} />
          ))}
        </div>
      </section>

      {homeData.comparePreview ? (
        <section className="border-y border-gray-200 bg-gray-50 py-16">
          <div className="container-custom">
            <SectionHeader
              title="Compare Coverage"
              subtitle="See where sources align, where emphasis shifts, and how a story is unfolding."
              centered
            />
            <CompareClusterCard cluster={homeData.comparePreview} />
          </div>
        </section>
      ) : null}

      <div className="container-custom py-12">
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <SectionHeader title="Latest Stories" subtitle="Fresh reporting from our active sources." />
            <div className="space-y-1">
              {homeData.latestStories.slice(0, 10).map((story) => (
                <StoryCardCompact key={story.id} story={story} />
              ))}
            </div>
          </div>

          <div>
            <SectionHeader title="Somalia" subtitle="Essential reporting from across the country." />
            <div className="space-y-4">
              {homeData.somaliaStories.slice(0, 5).length > 0 ? (
                homeData.somaliaStories.slice(0, 5).map((story) => (
                  <StoryCardCompact key={story.id} story={story} />
                ))
              ) : (
                <EmptyState title="No Somalia stories yet" message="Check back as new reporting comes in." />
              )}
            </div>
          </div>
        </div>
      </div>

      <section className="container-custom pb-16">
        <SectionHeader title="World" subtitle="Global developments with relevance to Somali readers." />
        {homeData.worldStories.length > 0 ? (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
            {homeData.worldStories.map((story) => (
              <StoryCardLarge key={story.id} story={story} />
            ))}
          </div>
        ) : (
          <EmptyState title="No world stories yet" message="Global coverage will appear here as stories are ingested." />
        )}
      </section>
    </div>
  )
}
