'use client'

import { CompareClusterCard } from '@/components/compare/CompareClusterCard'
import { HeroStoryCard } from '@/components/story/HeroStoryCard'
import { StoryCardCompact } from '@/components/story/StoryCardCompact'
import { StoryCardLarge } from '@/components/story/StoryCardLarge'
import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { useLanguage } from '@/components/language/LanguageProvider'
import { HomePageData } from '@/lib/types'

export function HomePageClient({ homeData }: { homeData: HomePageData | null }) {
  const { dictionary } = useLanguage()

  if (!homeData) {
    return (
      <div className="container-custom py-16 md:py-20">
        <LoadingSkeleton variant="hero" />
        <div className="mt-12 rounded-editorial border border-[#d8cab7] bg-white/80 p-8 text-center shadow-lift dark:border-white/10 dark:bg-[#182124]">
          <h1 className="mb-3 text-3xl font-bold md:text-4xl">
            {dictionary.states.frontPageUnavailableTitle}
          </h1>
          <p className="mx-auto max-w-2xl text-base leading-7 text-ink/70 dark:text-[#d8d2c9]">
            {dictionary.states.frontPageUnavailableMessage}
          </p>
        </div>
      </div>
    )
  }

  const topStories = (homeData.secondaryStories.length > 0
    ? homeData.secondaryStories
    : homeData.latestStories.filter((story) => story.id !== homeData.heroStory.id)
  ).slice(0, 3)
  const latestBrief = homeData.latestStories.filter((story) => story.id !== homeData.heroStory.id).slice(0, 3)

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <section className="border-b news-divider">
        <div className="container-custom py-8 md:py-14 xl:py-16">
          <div className="mb-8 grid gap-6 border-b news-divider pb-7 lg:grid-cols-[minmax(0,1.35fr)_minmax(18rem,0.65fr)] lg:items-end">
            <div className="space-y-3">
              <div className="eyebrow">{dictionary.home.eyebrow}</div>
              <h1 className="max-w-[16ch] text-[2.45rem] font-bold leading-[0.96] text-ink dark:text-[#fbf7f0] sm:text-[3.4rem] md:text-[4.15rem]">
                {dictionary.home.headline}
              </h1>
            </div>
            <p className="max-w-[34rem] text-[0.98rem] leading-7 text-ink/72 dark:text-[#d8d2c9] sm:text-base sm:leading-8">
              {dictionary.home.deck}
            </p>
          </div>

          <div className="grid gap-8 xl:grid-cols-[minmax(0,1.25fr)_22rem] xl:gap-10">
            <HeroStoryCard story={homeData.heroStory} />

            <aside className="section-surface p-5 md:p-6">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <div className="eyebrow">{dictionary.home.quickBriefTitle}</div>
                  <p className="mt-2 text-sm leading-6 text-ink/66 dark:text-[#d3cdc5]">
                    {dictionary.home.quickBriefSummary}
                  </p>
                </div>
              </div>
              <div className="divide-y divide-[#dfd4c3] dark:divide-white/10">
                {latestBrief.map((story) => (
                  <StoryCardCompact key={story.id} story={story} />
                ))}
              </div>
            </aside>
          </div>
        </div>
      </section>

      <section className="container-custom py-14 md:py-16 xl:py-20">
        <SectionHeader
          eyebrow={dictionary.home.eyebrow}
          title={dictionary.sections.topStories}
          subtitle={dictionary.sections.topStoriesSubtitle}
        />
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3 xl:gap-8">
          {topStories.map((story) => (
            <StoryCardLarge key={story.id} story={story} />
          ))}
        </div>
      </section>

      <section className="border-t news-divider bg-white/30 py-12 dark:bg-[#182124]/40 md:py-16 xl:py-20">
        <div className="container-custom">
          <SectionHeader
            title={dictionary.sections.latestStories}
            subtitle={dictionary.sections.latestStoriesSubtitle}
          />
          <div className="section-surface divide-y divide-[#dfd4c3] overflow-hidden dark:divide-white/10">
            {homeData.latestStories.slice(0, 8).map((story) => (
              <StoryCardCompact key={story.id} story={story} />
            ))}
          </div>
        </div>
      </section>

      <section className="container-custom py-12 md:py-16 xl:py-20">
        <SectionHeader
          title={dictionary.sections.compareCoverage}
          subtitle={dictionary.sections.compareCoverageSubtitle}
        />
        {homeData.comparePreview ? (
          <CompareClusterCard cluster={homeData.comparePreview} />
        ) : (
          <EmptyState
            title={dictionary.compare.noCoverageTitle}
            message={dictionary.compare.noCoverageMessage}
          />
        )}
      </section>

      <section className="border-t news-divider py-12 md:py-16 xl:py-20">
        <div className="container-custom">
          <SectionHeader
            title={dictionary.sections.somalia}
            subtitle={dictionary.sections.somaliaSubtitle}
          />
          {homeData.somaliaStories.length > 0 ? (
            <div className="grid grid-cols-1 gap-5 sm:gap-6 lg:grid-cols-3 xl:gap-8">
              {homeData.somaliaStories.slice(0, 3).map((story) => (
                <StoryCardLarge key={story.id} story={story} />
              ))}
            </div>
          ) : (
            <EmptyState
              title={dictionary.states.noSomaliaTitle}
              message={dictionary.states.noSomaliaMessage}
            />
          )}
        </div>
      </section>

      <section className="border-t news-divider bg-white/40 py-12 dark:bg-[#182124]/50 md:py-16 xl:py-20">
        <div className="container-custom">
          <SectionHeader title={dictionary.sections.world} subtitle={dictionary.sections.worldSubtitle} />
          {homeData.worldStories.length > 0 ? (
            <div className="grid grid-cols-1 gap-5 sm:gap-6 md:grid-cols-2 lg:grid-cols-4 xl:gap-8">
              {homeData.worldStories.slice(0, 4).map((story) => (
                <StoryCardLarge key={story.id} story={story} />
              ))}
            </div>
          ) : (
            <EmptyState title={dictionary.states.noWorldTitle} message={dictionary.states.noWorldMessage} />
          )}
        </div>
      </section>
    </div>
  )
}
