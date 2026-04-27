import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const alt = 'Warka Compare Coverage'
export const size = {
  width: 1200,
  height: 630,
}
export const contentType = 'image/png'

type BackendSource = {
  id: string
  name: string
  language?: string | null
}

type BackendStory = {
  source_id: string
  source?: BackendSource
}

type BackendCluster = {
  title?: string | null
  confidence_score?: number | null
  event_signature?: {
    confidence?: number
    source_count?: number
  } | null
  stories?: BackendStory[] | null
  sources?: BackendSource[] | null
}

async function getCluster(clusterId: string): Promise<BackendCluster | null> {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL
  if (!apiBaseUrl) {
    return null
  }

  try {
    const response = await fetch(`${apiBaseUrl}/api/clusters/${encodeURIComponent(clusterId)}`, {
      headers: {
        Accept: 'application/json',
      },
      next: {
        revalidate: 300,
      },
    })

    if (!response.ok) {
      return null
    }

    return (await response.json()) as BackendCluster
  } catch {
    return null
  }
}

function languageMix(cluster: BackendCluster | null) {
  const languages = new Set<string>()
  cluster?.stories?.forEach((story) => {
    const language = story.source?.language?.toLowerCase()
    if (language?.startsWith('so')) languages.add('SO')
    if (language?.startsWith('en')) languages.add('EN')
  })
  cluster?.sources?.forEach((source) => {
    const language = source.language?.toLowerCase()
    if (language?.startsWith('so')) languages.add('SO')
    if (language?.startsWith('en')) languages.add('EN')
  })

  if (languages.size === 0) return 'Language mix pending'
  return Array.from(languages).join(' + ')
}

function sourceCount(cluster: BackendCluster | null) {
  if (!cluster) return 0
  if (cluster.sources?.length) return cluster.sources.length
  if (cluster.event_signature?.source_count) return cluster.event_signature.source_count
  return new Set((cluster.stories || []).map((story) => story.source_id).filter(Boolean)).size
}

function confidenceLabel(cluster: BackendCluster | null) {
  const confidence = cluster?.confidence_score ?? cluster?.event_signature?.confidence
  if (!confidence) return 'New comparison'
  if (confidence >= 75) return `${confidence} high confidence`
  if (confidence >= 50) return `${confidence} medium confidence`
  return `${confidence} early signal`
}

export default async function OpenGraphImage({ params }: { params: { clusterId: string } }) {
  const cluster = await getCluster(params.clusterId)
  const headline = cluster?.title || 'Compare Coverage'
  const sources = sourceCount(cluster)
  const mix = languageMix(cluster)
  const confidence = confidenceLabel(cluster)

  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          background: '#FDF9F2',
          color: '#1A2A2F',
          padding: 64,
          fontFamily: 'Georgia, serif',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontFamily: 'Arial, sans-serif',
            fontSize: 24,
            letterSpacing: 5,
            textTransform: 'uppercase',
            color: '#A2472E',
          }}
        >
          <div>Compare Coverage</div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              color: '#1A2A2F',
              letterSpacing: 1,
              textTransform: 'none',
              fontSize: 30,
              fontWeight: 700,
            }}
          >
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 6,
                background: '#C25A3C',
              }}
            />
            Warka
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 30 }}>
          <div
            style={{
              maxWidth: 980,
              fontSize: headline.length > 95 ? 54 : 64,
              lineHeight: 1.03,
              fontWeight: 700,
              letterSpacing: -1,
            }}
          >
            {headline}
          </div>

          <div
            style={{
              display: 'flex',
              gap: 18,
              fontFamily: 'Arial, sans-serif',
              fontSize: 28,
              color: '#49443F',
            }}
          >
            <div style={pillStyle}>{sources || 'Multiple'} sources</div>
            <div style={pillStyle}>{mix}</div>
            <div style={pillStyle}>{confidence}</div>
          </div>
        </div>

        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderTop: '2px solid #DFD4C3',
            paddingTop: 26,
            fontFamily: 'Arial, sans-serif',
            color: '#736B63',
            fontSize: 24,
          }}
        >
          <div>Source-transparent Somali news comparison</div>
          <div>www.warkasta.com</div>
        </div>
      </div>
    ),
    size
  )
}

const pillStyle = {
  display: 'flex',
  border: '2px solid #DFD4C3',
  borderRadius: 999,
  padding: '12px 20px',
  background: 'rgba(255,255,255,0.75)',
} as const
