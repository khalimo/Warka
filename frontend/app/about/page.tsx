export const metadata = {
  title: 'About',
  description: 'Learn about Warka, our methodology, and how we approach source transparency.',
}

export default function AboutPage() {
  return (
    <div className="container-custom py-12">
      <div className="mx-auto max-w-3xl">
        <h1 className="mb-6 text-3xl font-bold">About Warka</h1>

        <div className="prose prose-lg max-w-none">
          <p className="lead">
            Warka is an independent news platform dedicated to providing comprehensive, transparent
            coverage of Somali and global affairs.
          </p>

          <h2>Our Mission</h2>
          <p>
            We believe that understanding multiple perspectives leads to better-informed readers and
            stronger democratic discourse. Warka aggregates news from multiple trusted sources,
            presents them transparently, and helps readers compare how different outlets cover the same events.
          </p>

          <h2>Somalia-First Journalism</h2>
          <p>
            While we cover important global stories, our primary focus is Somalia and the Somali diaspora.
            We prioritize stories that matter to Somali communities, from political developments in
            Mogadishu to diaspora achievements worldwide.
          </p>

          <h2>Source Transparency</h2>
          <p>
            Every story on Warka includes clear attribution to its original source. We believe readers
            should always know where information originates and have direct access to primary reporting.
          </p>

          <h2>Compare Coverage</h2>
          <p>
            Our signature feature highlights how different news organizations cover the same events.
            By presenting multiple perspectives side-by-side, we help readers identify areas of consensus,
            spot potential framing differences, and access a broader range of analysis.
          </p>

          <h2>Editorial Independence</h2>
          <p>
            Warka maintains strict editorial independence. We do not accept payment for coverage, and
            our source selection is based on journalistic relevance and credibility.
          </p>
        </div>
      </div>
    </div>
  )
}
