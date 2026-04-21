interface SectionHeaderProps {
  title: string
  subtitle?: string
  centered?: boolean
}

export function SectionHeader({ title, subtitle, centered = false }: SectionHeaderProps) {
  return (
    <div className={`mb-6 ${centered ? 'text-center' : ''}`}>
      <h2 className="text-2xl font-bold text-gray-900 md:text-3xl">{title}</h2>
      {subtitle ? <p className="mt-2 text-gray-600">{subtitle}</p> : null}
    </div>
  )
}
