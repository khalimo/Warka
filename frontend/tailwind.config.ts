import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        paper: '#FDF9F2',
        ink: '#1A2A2F',
        terracotta: '#C25A3C',
        sky: '#6B9EAB',
        acacia: '#7A8B5E',
        primary: {
          50: '#FBF0EB',
          100: '#F5DED5',
          200: '#E8BBAA',
          300: '#DA977E',
          400: '#CF755B',
          500: '#C25A3C',
          600: '#A2472E',
          700: '#7E3824',
          800: '#59281A',
          900: '#33170F',
        },
      },
      fontFamily: {
        serif: ['var(--font-newsreader)', 'Georgia', 'Cambria', 'Times New Roman', 'serif'],
        sans: ['var(--font-space-grotesk)', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        editorial: '0 22px 44px rgba(26, 42, 47, 0.10)',
        lift: '0 10px 24px rgba(26, 42, 47, 0.08)',
      },
      transitionTimingFunction: {
        editorial: 'cubic-bezier(0.22, 1, 0.36, 1)',
      },
      borderRadius: {
        editorial: '0.375rem',
      },
    },
  },
  plugins: [],
}

export default config
