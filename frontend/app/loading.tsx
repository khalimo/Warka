import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'

export default function Loading() {
  return (
    <div className="container-custom py-12">
      <LoadingSkeleton variant="hero" />
      <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="animate-pulse rounded-lg border border-gray-200 bg-white p-4">
            <div className="h-48 rounded-lg bg-gray-200" />
            <div className="mt-4 h-6 rounded bg-gray-200" />
            <div className="mt-2 h-4 w-5/6 rounded bg-gray-100" />
            <div className="mt-4 h-6 w-28 rounded-full bg-gray-100" />
          </div>
        ))}
      </div>
    </div>
  )
}
