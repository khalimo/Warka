'use client'

import Link from 'next/link'
import { CompareClusterCard } from '@/components/compare/CompareClusterCard'
import { TodayBrief } from '@/components/home/TodayBrief'
import { HeroStoryCard } from '@/components/story/HeroStoryCard'
import { StoryCardCompact } from '@/components/story/StoryCardCompact'
import { StoryCardLarge } from '@/components/story/StoryCardLarge'
import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { useLanguage } from '@/components/language/LanguageProvider'
import { HomePageData } from '@/lib/types'

export function HomePageClient({ homeData }: { homeData: HomePageData | null }) {
  const { lang, dictionary } = useLanguage()

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

  const latestBrief = homeData.latestStories.filter((story) => story.id !== homeData.heroStory.id).slice(0, 3)
  const compareClusters = homeData.compareClusters.length > 0
    ? homeData.compareClusters
    : homeData.comparePreview
      ? [homeData.comparePreview]
      : []
  const sourceCount = new Set([
    homeData.heroStory.source.id,
    ...homeData.latestStories.map((story) => story.source.id),
    ...homeData.somaliaStories.map((story) => story.source.id),
    ...homeData.worldStories.map((story) => story.source.id),
    ...compareClusters.flatMap((cluster) => cluster.sources.map((source) => source.id)),
  ]).size
  const coverageRails = [
    { key: 'humanitarian', label: lang === 'so' ? 'Bini’aadannimo' : 'Humanitarian' },
    { key: 'diaspora', label: lang === 'so' ? 'Qurbajoog' : 'Diaspora' },
    { key: 'economy', label: lang === 'so' ? 'Dhaqaale' : 'Economy' },
  ].map((rail) => ({
    ...rail,
    stories: homeData.latestStories
      .filter((story) => story.category === rail.key || story.source.category === rail.key)
      .slice(0, 2),
  }))

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <TodayBrief homeData={homeData} />

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

          <div className="mb-8 grid gap-3 sm:grid-cols-3">
            {[
              ['Active sources', sourceCount],
              ['Latest stories', homeData.latestStories.length],
              ['Coverage comparisons', compareClusters.length],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-editorial border border-[#ded2c0] bg-white/75 px-4 py-4 dark:border-white/10 dark:bg-[#182124]"
              >
                <div className="font-serif text-3xl font-bold text-ink dark:text-[#fbf7f0]">{value}</div>
                <div className="mt-1 text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-ink/48 dark:text-[#b7b1a8]">
                  {label}
                </div>
              </div>
            ))}
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

      <section className="container-custom py-12 md:py-16 xl:py-20">
        <SectionHeader
          title={dictionary.sections.compareCoverage}
          subtitle={dictionary.sections.compareCoverageSubtitle}
        />
        <div className="mb-6 grid gap-4 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
          <p className="max-w-3xl text-sm leading-7 text-ink/70 dark:text-[#d8d2ca]">
            Warka groups related reports so readers can see what different outlets agree on,
            emphasize, or leave out.
          </p>
          <Link
            href="/compare"
            className="inline-flex min-h-[44px] items-center justify-center rounded-full border border-primary-200 bg-primary-50 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.14em] text-primary-700 transition-colors duration-300 ease-editorial hover:bg-primary-100 dark:border-primary-900/50 dark:bg-primary-900/20 dark:text-primary-200 dark:hover:bg-primary-900/30"
          >
            View all comparisons
          </Link>
        </div>
        {compareClusters.length > 0 ? (
          <div className="space-y-6">
            {compareClusters.slice(0, 3).map((cluster) => (
              <CompareClusterCard key={cluster.id} cluster={cluster} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="Coverage comparisons are being prepared"
            message={`Stories have been collected, but Warka needs at least two related reports before comparison cards appear. Current homepage sample: ${homeData.latestStories.length} stories from ${sourceCount} sources.`}
          />
        )}
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

      <section className="border-t news-divider py-12 md:py-16 xl:py-20">
        <div className="container-custom">
          <SectionHeader
            title={dictionary.sections.coverageRails}
            subtitle={dictionary.sections.coverageRailsSubtitle}
          />
          <div className="grid gap-5 lg:grid-cols-3">
            {coverageRails.map((rail) => (
              <div
                key={rail.key}
                className="section-surface overflow-hidden p-0"
              >
                <div className="border-b news-divider px-5 py-4">
                  <div className="eyebrow">{rail.label}</div>
                </div>
                {rail.stories.length > 0 ? (
                  <div className="divide-y divide-[#dfd4c3] dark:divide-white/10">
                    {rail.stories.map((story) => (
                      <StoryCardCompact key={story.id} story={story} />
                    ))}
                  </div>
                ) : (
                  <div className="px-5 py-6 text-sm leading-6 text-ink/60 dark:text-[#cfc8bf]">
                    {dictionary.states.genericEmptyMessage}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
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

      <section className="border-t news-divider py-12 md:py-16">
        <div className="container-custom">
          <div className="rounded-editorial border border-[#d8cab7] bg-white/80 p-6 dark:border-white/10 dark:bg-[#182124] sm:p-8">
            <div className="grid gap-5 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
              <div>
                <div className="eyebrow">{dictionary.sections.sourcePulse}</div>
                <p className="mt-2 max-w-2xl text-sm leading-7 text-ink/68 dark:text-[#d8d2ca]">
                  {dictionary.sections.sourcePulseSubtitle}
                </p>
              </div>
              <Link
                href="/sources"
                className="inline-flex min-h-[44px] items-center justify-center rounded-full border border-primary-200 bg-primary-50 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.14em] text-primary-700 transition-colors duration-300 ease-editorial hover:bg-primary-100 dark:border-primary-900/50 dark:bg-primary-900/20 dark:text-primary-200 dark:hover:bg-primary-900/30"
              >
                {dictionary.nav.sources}
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
