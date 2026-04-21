import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="container-custom py-20 text-center">
      <h1 className="mb-4 text-4xl font-bold">404</h1>
      <h2 className="mb-4 text-2xl">Page not found</h2>
      <p className="mb-8 text-gray-600">The story you&apos;re looking for doesn&apos;t exist.</p>
      <Link href="/" className="text-primary-600 hover:underline">
        Return home →
      </Link>
    </div>
  )
}
