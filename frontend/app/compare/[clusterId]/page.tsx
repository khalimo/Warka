import type { Metadata } from 'next'
import { ClusterCoveragePageClient } from '@/components/pages/ClusterCoveragePageClient'
import { apiClient } from '@/lib/api'

type PageProps = {
  params: {
    clusterId: string
  }
}

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'
export const dynamic = 'force-dynamic'

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const cluster = await apiClient.getCompareCluster(params.clusterId)

  if (!cluster) {
    return { title: 'Coverage Not Found' }
  }

  const description = cluster.aiNeutralSummary || cluster.neutralSummary || cluster.commonFacts || 'Explore related coverage from Warka.'
  const url = `${siteUrl}/compare/${encodeURIComponent(cluster.id)}`
  const imageUrl = `${url}/opengraph-image`
  const title = `Compare Coverage: ${cluster.title}`

  return {
    title,
    description,
    alternates: {
      canonical: url,
    },
    openGraph: {
      title,
      description,
      type: 'article',
      url,
      images: [
        {
          url: imageUrl,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [imageUrl],
    },
  }
}

export default async function ClusterCoveragePage({ params }: PageProps) {
  const cluster = await apiClient.getCompareCluster(params.clusterId)

  const jsonLd = cluster
    ? {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        name: cluster.title,
        description: cluster.aiNeutralSummary || cluster.neutralSummary || cluster.commonFacts,
        url: `${siteUrl}/compare/${encodeURIComponent(cluster.id)}`,
        mainEntity: {
          '@type': 'ItemList',
          numberOfItems: cluster.stories.length,
          itemListElement: cluster.stories.map((story, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            url: `${siteUrl}/story/${story.slug}`,
            name: story.title,
          })),
        },
      }
    : null

  return (
    <>
      {cluster ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      ) : null}
      <ClusterCoveragePageClient cluster={cluster} />
    </>
  )
}
