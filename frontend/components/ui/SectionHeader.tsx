interface SectionHeaderProps {
  title: string
  subtitle?: string
  centered?: boolean
  eyebrow?: string
}

export function SectionHeader({ title, subtitle, centered = false, eyebrow }: SectionHeaderProps) {
  return (
    <div className={`mb-7 space-y-3 sm:mb-8 ${centered ? 'text-center' : ''}`}>
      {eyebrow ? <div className="eyebrow">{eyebrow}</div> : null}
      <div className={`flex ${centered ? 'justify-center' : 'justify-start'}`}>
        <span className="h-px w-16 bg-primary-400/80 dark:bg-primary-300/70" />
      </div>
      <h2 className="max-w-[18ch] text-[1.85rem] font-bold leading-[1.02] text-ink dark:text-[#fbf7f0] sm:text-[2.2rem] md:text-[2.75rem]">
        {title}
      </h2>
      {subtitle ? (
        <p className={`max-w-2xl text-[0.98rem] leading-7 text-ink/68 dark:text-[#d7d2ca] sm:text-base ${centered ? 'mx-auto' : ''}`}>
          {subtitle}
        </p>
      ) : null}
    </div>
  )
}
