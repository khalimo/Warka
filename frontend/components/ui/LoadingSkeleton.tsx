interface LoadingSkeletonProps {
  variant?: 'hero' | 'list' | 'story'
  count?: number
}

export function LoadingSkeleton({ variant = 'hero', count = 3 }: LoadingSkeletonProps) {
  if (variant === 'list') {
    return (
      <div className="space-y-4">
        {Array.from({ length: count }).map((_, index) => (
          <div key={index} className="animate-pulse border-b news-divider py-4">
            <div className="flex gap-4">
              <div className="h-24 w-24 rounded-editorial bg-[#eadfd0] dark:bg-[#233035]" />
              <div className="min-w-0 flex-1 space-y-3">
                <div className="h-5 w-4/5 rounded bg-[#e6dacb] dark:bg-[#233035]" />
                <div className="h-4 w-full rounded bg-[#f1e9de] dark:bg-[#1e292c]" />
                <div className="h-4 w-2/3 rounded bg-[#f1e9de] dark:bg-[#1e292c]" />
                <div className="h-6 w-32 rounded-full bg-[#f1e9de] dark:bg-[#1e292c]" />
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (variant === 'story') {
    return (
      <div className="animate-pulse">
        <div className="mb-4 h-6 w-48 rounded-full bg-[#efe4d6] dark:bg-[#1f2a2e]" />
        <div className="mb-4 h-12 w-11/12 rounded bg-[#e6dacb] dark:bg-[#243136]" />
        <div className="mb-8 h-8 w-3/4 rounded bg-[#efe4d6] dark:bg-[#1f2a2e]" />
        <div className="mb-8 h-[360px] rounded-editorial bg-[#e6dacb] dark:bg-[#243136]" />
        <div className="space-y-4">
          <div className="h-4 w-full rounded bg-[#efe4d6] dark:bg-[#1f2a2e]" />
          <div className="h-4 w-full rounded bg-[#efe4d6] dark:bg-[#1f2a2e]" />
          <div className="h-4 w-5/6 rounded bg-[#efe4d6] dark:bg-[#1f2a2e]" />
        </div>
      </div>
    )
  }

  return (
    <div className="animate-pulse">
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2 lg:gap-12">
        <div className="h-72 rounded-editorial bg-[#e6dacb] md:h-96 dark:bg-[#243136]" />
        <div className="space-y-4 self-center">
          <div className="h-5 w-24 rounded-full bg-primary-100 dark:bg-primary-900/40" />
          <div className="h-12 w-full rounded bg-[#e6dacb] dark:bg-[#243136]" />
          <div className="h-12 w-5/6 rounded bg-[#e6dacb] dark:bg-[#243136]" />
          <div className="h-5 w-full rounded bg-[#efe4d6] dark:bg-[#1f2a2e]" />
          <div className="h-5 w-4/5 rounded bg-[#efe4d6] dark:bg-[#1f2a2e]" />
          <div className="h-8 w-44 rounded-full bg-[#efe4d6] dark:bg-[#1f2a2e]" />
        </div>
      </div>
    </div>
  )
}
