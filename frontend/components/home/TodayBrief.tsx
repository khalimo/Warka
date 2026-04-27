'use client'

import Link from 'next/link'
import { AlertTriangle, GitCompareArrows, Newspaper, ShieldCheck } from 'lucide-react'
import { useLanguage } from '@/components/language/LanguageProvider'
import { getBriefingStats } from '@/lib/intelligence'
import { HomePageData } from '@/lib/types'

const icons = [Newspaper, GitCompareArrows, AlertTriangle, ShieldCheck]

export function TodayBrief({ homeData }: { homeData: HomePageData }) {
  const { dictionary } = useLanguage()
  const stats = getBriefingStats(homeData, dictionary)

  return (
    <section className="border-b news-divider bg-white/45 dark:bg-[#182124]/45">
      <div className="container-custom py-5 sm:py-6">
        <div className="grid gap-4 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] lg:items-center">
          <div>
            <div className="eyebrow">{dictionary.briefing.kicker}</div>
            <h2 className="mt-2 max-w-[20ch] text-[1.55rem] font-bold leading-tight text-ink dark:text-[#fbf7f0] sm:text-[1.9rem]">
              {dictionary.briefing.title}
            </h2>
            <p className="mt-2 max-w-[40rem] text-sm leading-7 text-ink/68 dark:text-[#d6d0c7] sm:text-base">
              {dictionary.briefing.deck}
            </p>
            <Link
              href="/briefing"
              className="mt-4 inline-flex min-h-[40px] items-center rounded-full border border-primary-200 bg-primary-50 px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-primary-700 transition-colors hover:bg-primary-100 dark:border-primary-900/50 dark:bg-primary-900/20 dark:text-primary-200"
            >
              {dictionary.nav.briefing}
            </Link>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {stats.map((item, index) => {
              const Icon = icons[index]

              return (
                <div
                  key={item.label}
                  className="rounded-editorial border border-[#dfd4c3] bg-white/85 p-4 shadow-lift dark:border-white/10 dark:bg-[#141d1f]"
                >
                  <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-full border border-primary-200 bg-primary-50 text-primary-700 dark:border-primary-900/60 dark:bg-primary-900/20 dark:text-primary-200">
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="font-serif text-3xl font-bold leading-none text-ink dark:text-[#fbf7f0]">
                    {item.value}
                  </div>
                  <div className="mt-2 text-[0.78rem] font-medium leading-5 text-ink/62 dark:text-[#c9c3ba]">
                    {item.label}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
