import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'

export default function LatestLoading() {
  return (
    <div className="container-custom py-12">
      <div className="mb-8 animate-pulse">
        <div className="h-10 w-56 rounded bg-gray-200" />
        <div className="mt-3 h-5 w-80 rounded bg-gray-100" />
      </div>
      <LoadingSkeleton variant="list" count={8} />
    </div>
  )
}
