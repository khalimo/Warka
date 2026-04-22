'use client'

export default function StoryError({
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="container-custom py-20 text-center">
      <h1 className="mb-4 text-3xl font-bold">We couldn&apos;t load this story</h1>
      <p className="mx-auto mb-8 max-w-2xl text-gray-600">
        The article is temporarily unavailable. Please try again in a moment.
      </p>
      <button
        onClick={reset}
        className="rounded-full bg-primary-600 px-5 py-3 font-medium text-white transition-colors hover:bg-primary-700"
      >
        Try again
      </button>
    </div>
  )
}
