import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton'

export default function StoryLoading() {
  return (
    <div className="container-custom py-12">
      <div className="mx-auto max-w-3xl">
        <LoadingSkeleton variant="story" />
      </div>
    </div>
  )
}
