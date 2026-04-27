'use client'

import Link from 'next/link'
import { FramingBadge } from '@/components/story/FramingBadge'
import { ReadingProgress } from '@/components/story/ReadingProgress'
import { SourceBadge } from '@/components/story/SourceBadge'
import { StoryLanguageBadge } from '@/components/story/StoryLanguageBadge'
import { StoryTranslationStatus } from '@/components/story/StoryTranslationStatus'
import { StoryTrustMethodologyPanel } from '@/components/trust/TrustMethodologyPanel'
import { useLanguage } from '@/components/language/LanguageProvider'
import { TimeAgo } from '@/components/ui/TimeAgo'
import { getStorySummaryBullets, getStoryTrustSignals } from '@/lib/intelligence'
import { getStoryContent, getStoryExcerpt, getStoryHeadline } from '@/lib/storyPresentation'
import { Story } from '@/lib/types'

export function StoryPageClient({ story }: { story: Story }) {
  const { lang, dictionary } = useLanguage()
  const summaryBullets = getStorySummaryBullets(story, lang, dictionary)
  const trustSignals = getStoryTrustSignals(story, dictionary)
  const storyContent = getStoryContent(story, lang)

  return (
    <article className="bg-paper dark:bg-[#141b1d]">
      <ReadingProgress />
      <div className="container-custom py-10 sm:py-12 md:py-16 xl:py-20">
        <div className="mx-auto max-w-[52rem]">
          <div className="mb-4 flex flex-wrap gap-2 sm:mb-5 sm:gap-3">
            <StoryLanguageBadge story={story} />
            <StoryTranslationStatus story={story} />
            <SourceBadge source={story.source} />
            {story.framing ? <FramingBadge framing={story.framing} /> : null}
          </div>

          <h1 className="max-w-[16ch] text-[2.3rem] font-bold leading-[0.96] text-ink dark:text-[#fbf7f0] sm:text-5xl lg:text-6xl">
            {getStoryHeadline(story, lang)}
          </h1>

          {story.excerpt ? (
            <p className="mt-5 max-w-[44rem] text-base leading-7 text-ink/70 dark:text-[#d6d0c7] sm:mt-6 sm:text-lg sm:leading-8 md:text-[1.4rem] md:leading-9">
              {getStoryExcerpt(story, lang)}
            </p>
          ) : null}

          <div className="mb-8 mt-6 flex flex-wrap items-center gap-x-3 gap-y-2 border-y news-divider py-4 text-[0.74rem] font-medium uppercase tracking-[0.14em] text-ink/50 dark:text-[#b9b2a8] sm:mb-10 sm:mt-8 sm:gap-x-4 sm:text-[0.78rem]">
            <span>{story.source.name}</span>
            <span className="hidden sm:inline">•</span>
            <TimeAgo date={story.publishedAt} />
            <span className="hidden sm:inline">•</span>
            <span>{story.region}</span>
          </div>

          <div className="mb-8 rounded-editorial border border-[#d8cab7] bg-white/80 p-4 text-sm leading-6 text-ink/68 dark:border-white/10 dark:bg-[#182124] dark:text-[#d8d2ca]">
            {story.lang === lang
              ? dictionary.translation.originalHelper
              : story.translations?.content?.[lang]
                ? dictionary.translation.translatedHelper
                : dictionary.translation.unavailableHelper}
          </div>

          <div className="mb-8 sm:mb-10">
            <StoryTrustMethodologyPanel story={story} lang={lang} dictionary={dictionary} />
          </div>

          <div className="mb-8 grid gap-4 sm:mb-10 lg:grid-cols-[minmax(0,1fr)_17rem]">
            <section className="rounded-editorial border border-acacia/25 bg-acacia/10 p-5 dark:border-acacia/20 dark:bg-acacia/10 sm:p-6">
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-[0.16em] text-acacia">
                {dictionary.storyTrust.keyPoints}
              </h2>
              <ul className="space-y-3">
                {summaryBullets.map((bullet) => (
                  <li
                    key={bullet}
                    className="grid grid-cols-[0.45rem_minmax(0,1fr)] gap-3 text-base leading-7 text-ink/78 dark:text-[#e0dbd2]"
                  >
                    <span className="mt-[0.72rem] h-1.5 w-1.5 rounded-full bg-acacia" />
                    <span>{bullet}</span>
                  </li>
                ))}
              </ul>
            </section>

            <aside className="rounded-editorial border border-[#d8cab7] bg-white/80 p-5 dark:border-white/10 dark:bg-[#182124] sm:p-6">
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-[0.16em] text-ink/58 dark:text-[#bbb4ab]">
                {dictionary.storyTrust.sourceRailTitle}
              </h2>
              <dl className="space-y-4">
                {trustSignals.map((signal) => (
                  <div key={signal.label}>
                    <dt className="text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#a9a39a]">
                      {signal.label}
                    </dt>
                    <dd className="mt-1 text-sm font-medium leading-6 text-ink/78 dark:text-[#e0dbd2]">
                      {signal.value}
                    </dd>
                  </div>
                ))}
                <div>
                  <dt className="text-[0.72rem] font-semibold uppercase tracking-[0.14em] text-ink/45 dark:text-[#a9a39a]">
                    {dictionary.storyTrust.published}
                  </dt>
                  <dd className="mt-1 text-sm font-medium leading-6 text-ink/78 dark:text-[#e0dbd2]">
                    <TimeAgo date={story.publishedAt} />
                  </dd>
                </div>
              </dl>
            </aside>
          </div>

          {story.imageUrl ? (
            <div className="mb-10 overflow-hidden rounded-editorial border border-[#d8cab7] shadow-editorial dark:border-white/10 sm:mb-12">
              <img
                src={story.imageUrl}
                alt={getStoryHeadline(story, lang)}
                className="aspect-[4/3] w-full object-cover sm:aspect-[16/10]"
              />
            </div>
          ) : null}

          {storyContent ? (
            <div
              className="prose prose-base max-w-none prose-headings:font-serif prose-headings:text-ink prose-p:max-w-[44rem] prose-p:text-[1rem] prose-p:leading-7 prose-p:text-ink/78 prose-a:text-primary-700 prose-strong:text-ink prose-li:text-ink/78 dark:prose-headings:text-[#fbf7f0] dark:prose-p:text-[#ddd7ce] dark:prose-a:text-primary-200 dark:prose-strong:text-[#fbf7f0] dark:prose-li:text-[#ddd7ce] sm:prose-lg sm:prose-p:text-[1.06rem] sm:prose-p:leading-8"
              dangerouslySetInnerHTML={{ __html: storyContent }}
            />
          ) : null}

          <div className="mt-12 border-t news-divider pt-7 sm:mt-14 sm:pt-8">
            <Link
              href={story.originalUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex min-h-[44px] items-center rounded-full border border-primary-200 bg-primary-50 px-5 py-2.5 text-sm font-semibold uppercase tracking-[0.14em] text-primary-700 transition-colors duration-300 ease-editorial hover:bg-primary-100 dark:border-primary-900/50 dark:bg-primary-900/20 dark:text-primary-200 dark:hover:bg-primary-900/30"
            >
              {dictionary.pages.story.readOriginalPrefix} {story.source.name} →
            </Link>
          </div>
        </div>
      </div>
    </article>
  )
}
