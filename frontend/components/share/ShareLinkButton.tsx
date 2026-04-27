'use client'

import { useMemo, useState } from 'react'
import { Check, Share2 } from 'lucide-react'
import { useLanguage } from '@/components/language/LanguageProvider'

type Props = {
  path: string
  title: string
  summary?: string
  compact?: boolean
}

export function ShareLinkButton({ path, title, summary, compact = false }: Props) {
  const { dictionary } = useLanguage()
  const [copied, setCopied] = useState(false)
  const fallbackUrl = path.startsWith('http') ? path : path
  const shareUrl = useMemo(() => {
    if (typeof window === 'undefined') {
      return fallbackUrl
    }
    return path.startsWith('http') ? path : `${window.location.origin}${path}`
  }, [fallbackUrl, path])

  async function handleShare() {
    try {
      if (typeof navigator !== 'undefined' && navigator.share) {
        await navigator.share({
          title,
          text: summary || dictionary.share.defaultText,
          url: shareUrl,
        })
        return
      }

      await navigator.clipboard.writeText(shareUrl)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1800)
    } catch {
      setCopied(false)
    }
  }

  return (
    <button
      type="button"
      onClick={handleShare}
      className={`inline-flex min-h-[40px] items-center justify-center gap-2 rounded-full border border-[#d8cab7] bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-ink transition-colors hover:bg-paper dark:border-white/10 dark:bg-[#141d1f] dark:text-[#fbf7f0] ${
        compact ? 'px-3' : 'sm:px-5'
      }`}
    >
      {copied ? <Check className="h-3.5 w-3.5" /> : <Share2 className="h-3.5 w-3.5" />}
      {copied ? dictionary.share.copied : dictionary.share.share}
    </button>
  )
}
