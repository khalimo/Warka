interface EmptyStateProps {
  title?: string
  message?: string
}

export function EmptyState({
  title = 'No stories found',
  message = 'Check back later for updates.',
}: EmptyStateProps) {
  return (
    <div className="py-12 text-center">
      <p className="text-gray-500">{title}</p>
      <p className="mt-1 text-sm text-gray-400">{message}</p>
    </div>
  )
}
