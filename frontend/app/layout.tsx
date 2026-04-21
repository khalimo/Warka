import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { SiteHeader } from '@/components/layout/SiteHeader'
import { SiteFooter } from '@/components/layout/SiteFooter'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: 'Warka | Independent Somali News',
    template: '%s | Warka',
  },
  description: 'Independent Somali news with source transparency and coverage comparison.',
  openGraph: {
    type: 'website',
    locale: 'en_SO',
    siteName: 'Warka',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} flex min-h-screen flex-col`}>
        <Providers>
          <SiteHeader />
          <main className="flex-grow">{children}</main>
          <SiteFooter />
        </Providers>
      </body>
    </html>
  )
}
