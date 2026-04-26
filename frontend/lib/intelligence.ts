import { AppLanguage, UIStrings } from './i18n'
import { CompareCluster, HomePageData, Source, Story } from './types'

export function uniqueSources(stories: Story[]): Source[] {
  const sources = new Map<string, Source>()

  stories.forEach((story) => {
    sources.set(story.source.id, story.source)
  })

  return Array.from(sources.values())
}

export function languageMix(stories: Story[], dictionary: UIStrings) {
  const languages = new Set(stories.map((story) => story.lang))

  if (languages.has('so') && languages.has('en')) {
    return `${dictionary.languages.shortSo} + ${dictionary.languages.shortEn}`
  }

  if (languages.has('so')) {
    return dictionary.languages.shortSo
  }

  return dictionary.languages.shortEn
}

export function getBriefingStats(homeData: HomePageData, dictionary: UIStrings) {
  const stories = [
    homeData.heroStory,
    ...homeData.secondaryStories,
    ...homeData.latestStories,
    ...homeData.somaliaStories,
    ...homeData.worldStories,
  ]
  const sources = uniqueSources(stories)
  const breakingStories = stories.filter((story) => story.isBreaking)
  const compareCount = homeData.compareClusters.length || (homeData.comparePreview ? 1 : 0)
  const importantCount = Math.min(5, new Set(stories.map((story) => story.id)).size)

  return [
    {
      value: importantCount,
      label: dictionary.briefing.importantStories,
    },
    {
      value: compareCount,
      label: dictionary.briefing.comparedIssues,
    },
    {
      value: breakingStories.length,
      label: dictionary.briefing.breakingStories,
    },
    {
      value: sources.length,
      label: dictionary.briefing.verifiedSources,
    },
  ]
}

export function getCompareSourceStats(cluster: CompareCluster, dictionary: UIStrings) {
  return [
    {
      label: dictionary.compare.sourceCount,
      value: `${cluster.sources.length}`,
    },
    {
      label: dictionary.compare.languageMix,
      value: languageMix(cluster.stories, dictionary),
    },
    {
      label: dictionary.compare.storyCount,
      value: `${cluster.stories.length}`,
    },
  ]
}

export function getStorySummaryBullets(story: Story, lang: AppLanguage, dictionary: UIStrings) {
  const preferredSummary = story.translations?.summary?.[lang] || story.summary || story.excerpt
  const sentences = preferredSummary
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean)

  if (sentences.length >= 3) {
    return sentences.slice(0, 4)
  }

  return [
    story.title,
    story.excerpt,
    `${dictionary.storyTrust.sourcePrefix} ${story.source.name}`,
  ].filter(Boolean).slice(0, 3)
}

export function getStoryTrustSignals(story: Story, dictionary: UIStrings) {
  return [
    {
      label: dictionary.storyTrust.source,
      value: story.source.name,
    },
    {
      label: dictionary.storyTrust.language,
      value: story.lang === 'so' ? dictionary.languages.so : dictionary.languages.en,
    },
    {
      label: dictionary.storyTrust.reportType,
      value: story.source.category === 'international'
        ? dictionary.storyTrust.wireOrInternational
        : dictionary.storyTrust.originalOrLocal,
    },
  ]
}
