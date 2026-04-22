import { CompareClusterCard } from '@/components/compare/CompareClusterCard'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { EmptyState } from '@/components/ui/EmptyState'
import { HeroStoryCard } from '@/components/story/HeroStoryCard'
import { StoryCardCompact } from '@/components/story/StoryCardCompact'
import { StoryCardLarge } from '@/components/story/StoryCardLarge'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Independent Somali News',
  description: 'Independent Somali news with source transparency and multi-source coverage comparison.',
}

export const dynamic = 'force-dynamic'

export default async function HomePage() {
  const homeData = await apiClient.getHomePage()

  if (!homeData) {
    return (
      <div className="container-custom py-16 md:py-20">
        <LoadingSkeleton variant="hero" />
        <div className="mt-12 rounded-editorial border border-[#d8cab7] bg-white/80 p-8 text-center shadow-lift dark:border-white/10 dark:bg-[#182124]">
          <h1 className="mb-3 text-3xl font-bold md:text-4xl">We couldn&apos;t load the front page just now</h1>
          <p className="mx-auto max-w-2xl text-base leading-7 text-ink/70 dark:text-[#d8d2c9]">
            The latest stories are temporarily unavailable. Please try again in a moment.
          </p>
        </div>
      </div>
    )
  }

  const latestWithoutHero = homeData.latestStories.filter((story) => story.id !== homeData.heroStory.id)
  const editorsPicks = latestWithoutHero.slice(0, 3)
  const breakingStories = latestWithoutHero.filter((story) => story.isBreaking).slice(0, 3)
  const breakingRail = (breakingStories.length > 0 ? breakingStories : latestWithoutHero.slice(3, 6)).slice(0, 3)

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <section className="border-b news-divider">
        <div className="container-custom py-8 md:py-14 xl:py-16">
          <div className="mb-8 flex flex-col gap-4 border-b news-divider pb-6 md:flex-row md:items-end md:justify-between">
            <div className="space-y-3">
              <div className="eyebrow">Warka Front Page</div>
              <h1 className="max-w-4xl text-[2.35rem] font-bold leading-[0.96] sm:text-5xl md:text-6xl xl:text-7xl">
                Calm, distinctive coverage of Somalia and the world around it.
              </h1>
            </div>
            <p className="max-w-md text-sm leading-6 text-ink/70 dark:text-[#d8d2c9] sm:leading-7">
              The lead story takes the floor, supporting reporting stays easy to scan, and comparison stays close at hand.
            </p>
          </div>

          <div className="grid gap-8 lg:gap-10 xl:grid-cols-[minmax(0,1.45fr)_21rem]">
            <div className="space-y-8 md:space-y-10">
              <div className="grid gap-6 sm:gap-8 lg:grid-cols-[minmax(0,1.12fr)_18rem] xl:gap-10">
                <HeroStoryCard story={homeData.heroStory} />

                <aside className="space-y-4 border-t news-divider pt-5 lg:space-y-5 lg:border-l lg:border-t-0 lg:pl-6 lg:pt-0">
                  <div className="flex items-center justify-between">
                    <span className="eyebrow">Editor&apos;s Picks</span>
                    <span className="text-xs uppercase tracking-[0.16em] text-ink/45 dark:text-[#b3aea6]">
                      Curated
                    </span>
                  </div>
                  <div className="space-y-2">
                    {editorsPicks.map((story) => (
                      <StoryCardCompact key={story.id} story={story} />
                    ))}
                  </div>
                </aside>
              </div>

              <div className="grid gap-5 sm:gap-6 md:grid-cols-3 xl:gap-8">
                {homeData.secondaryStories.map((story) => (
                  <StoryCardLarge key={story.id} story={story} />
                ))}
              </div>
            </div>

            <aside className="space-y-5 border-t news-divider pt-6 xl:space-y-6 xl:border-l xl:pl-8 xl:pt-0">
              <div className="section-surface p-5 md:p-6">
                <div className="mb-4 flex items-center justify-between">
                  <span className="eyebrow">Breaking</span>
                  <span className="signature-chip">Live monitor</span>
                </div>
                <div className="space-y-4">
                  {breakingRail.map((story, index) => (
                    <div
                      key={story.id}
                      className={`pb-4 ${index < breakingRail.length - 1 ? 'border-b news-divider' : ''}`}
                    >
                      <StoryCardCompact story={story} />
                    </div>
                  ))}
                </div>
              </div>

              {homeData.comparePreview ? (
                <div className="space-y-4">
                  <div className="mb-4 flex items-center justify-between">
                    <span className="eyebrow">Signature feature</span>
                    <span className="signature-chip">Compare Coverage</span>
                  </div>
                  <CompareClusterCard cluster={homeData.comparePreview} />
                </div>
              ) : null}
            </aside>
          </div>
        </div>
      </section>

      <section className="container-custom py-14 md:py-16 xl:py-20">
        <SectionHeader
          title="Top Stories"
          subtitle="The biggest developments shaping Somalia and the wider region."
        />
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3 xl:gap-8">
          {latestWithoutHero.slice(0, 3).map((story) => (
            <StoryCardLarge key={story.id} story={story} />
          ))}
        </div>
      </section>

      <div className="container-custom py-12 md:py-16 xl:py-20">
        <div className="grid grid-cols-1 gap-10 md:gap-12 lg:grid-cols-[minmax(0,1.45fr)_minmax(19rem,0.8fr)] xl:gap-14">
          <div className="lg:col-span-2">
            <SectionHeader title="Latest Stories" subtitle="Fresh reporting from our active sources." />
            <div className="section-surface divide-y divide-[#dfd4c3] overflow-hidden dark:divide-white/10">
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

      <section className="border-t news-divider bg-white/40 py-12 dark:bg-[#182124]/50 md:py-16 xl:py-20">
        <div className="container-custom">
          <SectionHeader title="World" subtitle="Global developments with relevance to Somali readers." />
          {homeData.worldStories.length > 0 ? (
            <div className="grid grid-cols-1 gap-5 sm:gap-6 md:grid-cols-2 lg:grid-cols-4 xl:gap-8">
              {homeData.worldStories.map((story) => (
                <StoryCardLarge key={story.id} story={story} />
              ))}
            </div>
          ) : (
            <EmptyState title="No world stories yet" message="Global coverage will appear here as stories are ingested." />
          )}
        </div>
      </section>
    </div>
  )
}
