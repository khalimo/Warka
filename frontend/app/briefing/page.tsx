import { BriefingPageClient } from '@/components/pages/BriefingPageClient'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Today’s Somali Briefing',
  description: 'A calm daily briefing of current Somali stories, active coverage clusters, and source-transparent context.',
}

export const dynamic = 'force-dynamic'

export default async function BriefingPage() {
  const [homeData, clusters, latest, sources] = await Promise.all([
    apiClient.getHomePage(),
    apiClient.getCompareClusters(8, 0, undefined, undefined, true),
    apiClient.getLatestStories(60, 0),
    apiClient.getSources(),
  ])

  return (
    <BriefingPageClient
      homeData={homeData}
      clusters={clusters?.items || []}
      latestStories={latest?.items || []}
      activeSourceCount={sources?.length || homeData?.diagnostics.activeSourceCount || 0}
      apiUnavailable={!homeData && !latest && !clusters}
    />
  )
}
