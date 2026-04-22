'use client'

import Link from 'next/link'
import { useLanguage } from '@/components/language/LanguageProvider'

export function SiteFooter() {
  const { dictionary } = useLanguage()

  return (
    <footer className="mt-auto border-t border-white/10 bg-[#1a2326] text-[#d8d2ca]">
      <div className="container-custom py-14 md:py-16">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-4">
          <div className="md:col-span-2">
            <div className="eyebrow mb-3 text-primary-300">{dictionary.brand.edition}</div>
            <span className="font-serif text-3xl font-bold text-[#fbf7f0]">{dictionary.brand.name}</span>
            <p className="mt-5 max-w-md text-sm leading-7 text-[#cfc8bf]">
              {dictionary.brand.description}
            </p>
          </div>
          <div>
            <h3 className="mb-4 text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-[#fbf7f0]">
              {dictionary.footer.sectionsHeading}
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/somalia" className="editorial-link hover:text-white">
                  {dictionary.nav.somalia}
                </Link>
              </li>
              <li>
                <Link href="/world" className="editorial-link hover:text-white">
                  {dictionary.nav.world}
                </Link>
              </li>
              <li>
                <Link href="/compare" className="editorial-link hover:text-white">
                  {dictionary.sections.compareCoverage}
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-4 text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-[#fbf7f0]">
              {dictionary.footer.aboutHeading}
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/about" className="editorial-link hover:text-white">
                  {dictionary.footer.methodology}
                </Link>
              </li>
              <li>
                <Link href="/about" className="editorial-link hover:text-white">
                  {dictionary.footer.transparency}
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-10 border-t border-white/10 pt-8 text-center text-sm text-[#bfb9b0]">
          © {new Date().getFullYear()} {dictionary.brand.name}. {dictionary.footer.rightsReserved}
        </div>
      </div>
    </footer>
  )
}
