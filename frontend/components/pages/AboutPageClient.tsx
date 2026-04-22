'use client'

import { useLanguage } from '@/components/language/LanguageProvider'

export function AboutPageClient() {
  const { dictionary } = useLanguage()
  const about = dictionary.pages.about

  const sections = [
    { title: about.missionTitle, body: about.missionBody },
    { title: about.somaliaTitle, body: about.somaliaBody },
    { title: about.transparencyTitle, body: about.transparencyBody },
    { title: about.compareTitle, body: about.compareBody },
    { title: about.independenceTitle, body: about.independenceBody },
  ]

  return (
    <div className="bg-paper dark:bg-[#141b1d]">
      <div className="container-custom py-12 md:py-16 xl:py-20">
        <div className="mx-auto max-w-3xl">
          <div className="eyebrow mb-4">{dictionary.footer.aboutHeading}</div>
          <h1 className="mb-6 text-[2.4rem] font-bold leading-[0.98] text-ink dark:text-[#fbf7f0] sm:text-[3.2rem]">
            {about.title}
          </h1>

          <div className="prose prose-lg max-w-none prose-headings:font-serif prose-headings:text-ink prose-p:text-ink/78 prose-p:leading-8 dark:prose-headings:text-[#fbf7f0] dark:prose-p:text-[#d8d2ca]">
            <p className="lead max-w-[40rem] text-[1.08rem] leading-8 text-ink/78 dark:text-[#d8d2ca]">
              {about.lead}
            </p>

            {sections.map((section) => (
              <div key={section.title}>
                <h2>{section.title}</h2>
                <p>{section.body}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
