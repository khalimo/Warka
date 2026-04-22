'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Menu, Newspaper, X } from 'lucide-react'
import clsx from 'clsx'

const navigation = [
  { name: 'Home', href: '/' },
  { name: 'Latest', href: '/latest' },
  { name: 'Somalia', href: '/somalia' },
  { name: 'World', href: '/world' },
  { name: 'Compare', href: '/compare' },
  { name: 'About', href: '/about' },
]

export function SiteHeader() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 border-b news-divider bg-paper/95 backdrop-blur dark:bg-[#141b1d]/95">
      <div className="border-b news-divider">
        <div className="container-custom flex items-center justify-between py-2 text-[0.68rem] font-medium uppercase tracking-[0.16em] text-ink/60 dark:text-[#c8c2ba]">
          <span>Somali &amp; Global Report</span>
          <span className="hidden md:inline">Source transparency and comparison</span>
        </div>
      </div>
      <nav className="container-custom">
        <div className="flex h-20 items-center justify-between">
          <Link href="/" className="group flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-editorial border border-primary-200 bg-primary-50 text-primary-600 transition-colors group-hover:border-primary-300 dark:border-primary-900/60 dark:bg-primary-900/20 dark:text-primary-200">
              <Newspaper className="h-5 w-5" />
            </span>
            <div>
              <div className="font-serif text-[2rem] font-bold leading-none tracking-[-0.03em] text-ink dark:text-[#fbf7f0]">
                Warka
              </div>
              <div className="mt-1 text-[0.68rem] font-medium uppercase tracking-[0.2em] text-ink/55 dark:text-[#bfb9b0]">
                Reader Edition
              </div>
            </div>
          </Link>

          <div className="hidden items-center gap-8 md:flex">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={clsx(
                  'editorial-link border-b border-transparent pb-1 text-sm font-medium tracking-[0.01em]',
                  pathname === item.href
                    ? 'border-primary-500 text-primary-600 dark:border-primary-300 dark:text-primary-200'
                    : 'text-ink/78 hover:border-primary-200 hover:text-primary-600 dark:text-[#ddd7cf] dark:hover:border-primary-800 dark:hover:text-primary-200'
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>

          <div className="hidden items-center gap-3 md:flex">
            <span className="rounded-full border border-sky/30 bg-sky/10 px-3 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-sky dark:border-sky/20 dark:bg-sky/10 dark:text-sky">
              Reader Mode
            </span>
          </div>

          <button
            onClick={() => setMobileMenuOpen((open) => !open)}
            className="rounded-editorial border border-transparent p-2 text-ink hover:border-primary-200 hover:bg-white/70 dark:text-[#f3ede5] dark:hover:border-primary-900/50 dark:hover:bg-[#182124] md:hidden"
            aria-label="Toggle navigation"
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {mobileMenuOpen ? (
          <div className="border-t news-divider py-5 md:hidden">
            <div className="mb-3">
              <span className="rounded-full border border-sky/30 bg-sky/10 px-3 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.16em] text-sky dark:border-sky/20 dark:bg-sky/10 dark:text-sky">
                Reader Mode
              </span>
            </div>
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={clsx(
                  'block border-b news-divider py-3 text-sm font-medium',
                  pathname === item.href
                    ? 'text-primary-600 dark:text-primary-200'
                    : 'text-ink/80 hover:text-primary-600 dark:text-[#ddd7cf] dark:hover:text-primary-200'
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>
        ) : null}
      </nav>
    </header>
  )
}
