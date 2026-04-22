'use client'

import { StoryCardCompact } from '@/components/story/StoryCardCompact'
import { StoryCardLarge } from '@/components/story/StoryCardLarge'
import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { useLanguage } from '@/components/language/LanguageProvider'
import { Story } from '@/lib/types'

type CollectionVariant = 'latest' | 'somalia' | 'world'

export function StoryCollectionPageClient({
  variant,
  stories,
  failed = false,
}: {
  variant: CollectionVariant
  stories: Story[]
  failed?: boolean
}) {
  const { dictionary } = useLanguage()
  const page = dictionary.pages[variant]

  if (failed) {
    return (
      <div className="container-custom py-16 md:py-20">
        <LoadingSkeleton variant={variant === 'latest' ? 'list' : 'hero'} count={6} />
        <div className="mt-8">
          <EmptyState title={dictionary.pages.latest.loadErrorTitle} message={dictionary.pages.latest.loadErrorMessage} />
        </div>
      </div>
    )
  }

  if (stories.length === 0) {
    const title = variant === 'latest' ? dictionary.pages.latest.emptyTitle : dictionary.states.genericEmptyTitle
    const message =
      variant === 'latest' ? dictionary.pages.latest.emptyMessage : dictionary.states.genericEmptyMessage

    return (
      <div className="container-custom py-16 md:py-20">
        <EmptyState title={title} message={message} />
      </div>
    )
  }

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <section className="border-b news-divider">
        <div className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
          <div className="mx-auto max-w-4xl">
            <SectionHeader title={page.title} subtitle={page.subtitle} />
          </div>
        </div>
      </section>

      <section className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
        <div className="mx-auto max-w-5xl">
          {variant === 'latest' ? (
            <div className="section-surface divide-y divide-[#dfd4c3] overflow-hidden dark:divide-white/10">
              {stories.map((story) => (
                <StoryCardCompact key={story.id} story={story} />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-5 sm:gap-6 md:grid-cols-2 xl:grid-cols-3 xl:gap-8">
              {stories.map((story) => (
                <StoryCardLarge key={story.id} story={story} />
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
