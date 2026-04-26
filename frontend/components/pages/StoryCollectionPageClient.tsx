'use client'

import { useMemo, useState } from 'react'
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
  const [query, setQuery] = useState('')
  const [languageFilter, setLanguageFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')

  const categories = useMemo(
    () => Array.from(new Set(stories.map((story) => story.category).filter(Boolean))).sort(),
    [stories]
  )
  const filteredStories = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()
    return stories.filter((story) => {
      if (languageFilter !== 'all' && story.lang !== languageFilter) {
        return false
      }
      if (categoryFilter !== 'all' && story.category !== categoryFilter) {
        return false
      }
      if (!normalizedQuery) {
        return true
      }
      return `${story.title} ${story.excerpt} ${story.source.name} ${story.category}`
        .toLowerCase()
        .includes(normalizedQuery)
    })
  }, [categoryFilter, languageFilter, query, stories])

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
          <div className="mb-8 grid gap-3 rounded-editorial border border-[#d8cab7] bg-white/80 p-4 dark:border-white/10 dark:bg-[#182124] md:grid-cols-[minmax(0,1fr)_12rem_12rem]">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={variant === 'latest' ? dictionary.filters.searchLatest : `${dictionary.filters.searchSection}: ${page.title}`}
              className="min-h-[44px] rounded-editorial border border-[#d8cab7] bg-white px-3 text-sm text-ink outline-none transition focus:border-primary-300 dark:border-white/10 dark:bg-[#141b1d] dark:text-[#fbf7f0]"
            />
            <select
              value={languageFilter}
              onChange={(event) => setLanguageFilter(event.target.value)}
              className="min-h-[44px] rounded-editorial border border-[#d8cab7] bg-white px-3 text-sm text-ink outline-none transition focus:border-primary-300 dark:border-white/10 dark:bg-[#141b1d] dark:text-[#fbf7f0]"
            >
              <option value="all">{dictionary.filters.allLanguages}</option>
              <option value="so">{dictionary.languages.so}</option>
              <option value="en">{dictionary.languages.en}</option>
            </select>
            <select
              value={categoryFilter}
              onChange={(event) => setCategoryFilter(event.target.value)}
              className="min-h-[44px] rounded-editorial border border-[#d8cab7] bg-white px-3 text-sm capitalize text-ink outline-none transition focus:border-primary-300 dark:border-white/10 dark:bg-[#141b1d] dark:text-[#fbf7f0]"
            >
              <option value="all">{dictionary.filters.allCoverage}</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
          {filteredStories.length === 0 ? (
            <EmptyState title={dictionary.states.genericEmptyTitle} message={dictionary.states.genericEmptyMessage} />
          ) : null}
          {variant === 'latest' ? (
            <div className="section-surface divide-y divide-[#dfd4c3] overflow-hidden dark:divide-white/10">
              {filteredStories.map((story) => (
                <StoryCardCompact key={story.id} story={story} />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-5 sm:gap-6 md:grid-cols-2 xl:grid-cols-3 xl:gap-8">
              {filteredStories.map((story) => (
                <StoryCardLarge key={story.id} story={story} />
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
