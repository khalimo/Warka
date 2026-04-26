import { AppLanguage } from './i18n'
import { Story } from './types'

export function getStoryHeadline(story: Story, lang: AppLanguage) {
  return story.translations?.headline?.[lang] || story.title
}

export function getStoryExcerpt(story: Story, lang: AppLanguage) {
  return story.translations?.excerpt?.[lang] || story.excerpt
}

export function getStoryContent(story: Story, lang: AppLanguage) {
  return story.translations?.content?.[lang] || story.content
}

export function hasStoryTranslation(story: Story, lang: AppLanguage) {
  return Boolean(
    story.translations?.headline?.[lang] ||
      story.translations?.excerpt?.[lang] ||
      story.translations?.summary?.[lang] ||
      story.translations?.content?.[lang]
  )
}

export function isOriginalStoryLanguage(story: Story, lang: AppLanguage) {
  return story.lang === lang
}
