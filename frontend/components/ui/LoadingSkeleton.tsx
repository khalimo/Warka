export function LoadingSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="mb-8 h-96 rounded-lg bg-gray-200" />
      <div className="space-y-4">
        <div className="h-8 w-3/4 rounded bg-gray-200" />
        <div className="h-4 w-1/2 rounded bg-gray-200" />
        <div className="h-4 w-full rounded bg-gray-200" />
      </div>
    </div>
  )
}
