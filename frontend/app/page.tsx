import { HomePageClient } from '@/components/home/HomePageClient'
import { apiClient } from '@/lib/api'

export const metadata = {
  title: 'Independent Somali News',
  description: 'Independent Somali news with source transparency and multi-source coverage comparison.',
}

export const dynamic = 'force-dynamic'

export default async function HomePage() {
  const homeData = await apiClient.getHomePage()

  return <HomePageClient homeData={homeData} />
}
