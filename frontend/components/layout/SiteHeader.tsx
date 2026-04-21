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
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/95 backdrop-blur">
      <nav className="container-custom">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-50 text-primary-600">
              <Newspaper className="h-5 w-5" />
            </span>
            <span className="font-serif text-xl font-bold">Warka</span>
          </Link>

          <div className="hidden items-center gap-8 md:flex">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={clsx(
                  'text-sm font-medium transition-colors',
                  pathname === item.href ? 'text-primary-600' : 'text-gray-700 hover:text-primary-600'
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>

          <div className="hidden items-center gap-3 md:flex">
            <span className="rounded-full border border-gray-200 px-3 py-1 text-xs font-medium text-gray-600">
              Reader Mode
            </span>
          </div>

          <button
            onClick={() => setMobileMenuOpen((open) => !open)}
            className="rounded-md p-2 text-gray-700 hover:bg-gray-100 md:hidden"
            aria-label="Toggle navigation"
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {mobileMenuOpen ? (
          <div className="border-t border-gray-100 py-4 md:hidden">
            <div className="mb-3">
              <span className="rounded-full border border-gray-200 px-3 py-1 text-xs font-medium text-gray-600">
                Reader Mode
              </span>
            </div>
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={clsx(
                  'block py-2 text-sm font-medium',
                  pathname === item.href ? 'text-primary-600' : 'text-gray-700 hover:text-primary-600'
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
