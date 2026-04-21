import Link from 'next/link'

export function SiteFooter() {
  return (
    <footer className="mt-auto bg-gray-950 text-gray-400">
      <div className="container-custom py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          <div className="md:col-span-2">
            <span className="font-serif text-2xl font-bold text-white">Warka</span>
            <p className="mt-4 max-w-md text-sm leading-6">
              Independent Somali news with source transparency, multi-source comparison, and a cleaner way
              to understand what matters.
            </p>
          </div>
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-white">Sections</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/somalia" className="hover:text-white">
                  Somalia
                </Link>
              </li>
              <li>
                <Link href="/world" className="hover:text-white">
                  World
                </Link>
              </li>
              <li>
                <Link href="/compare" className="hover:text-white">
                  Compare Coverage
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-white">About</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/about" className="hover:text-white">
                  Methodology
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-white">
                  Source Transparency
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-8 border-t border-gray-800 pt-8 text-center text-sm">
          © {new Date().getFullYear()} Warka. All rights reserved.
        </div>
      </div>
    </footer>
  )
}
