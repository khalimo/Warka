'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="container-custom py-20 text-center">
      <h1 className="mb-4 text-3xl font-bold">Something went wrong</h1>
      <p className="mx-auto mb-8 max-w-2xl text-gray-600">
        We couldn&apos;t load this page right now. Please try again in a moment.
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
