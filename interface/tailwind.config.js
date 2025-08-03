import typography from '@tailwindcss/typography'

export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '2rem',
        lg: '4rem'
      }
    },
    extend: {
      screens: {
        xs: '375px'
      },
      colors: {
        primary: {
          DEFAULT: '#ff7c0a',
          dark: '#db6b00'
        },
        secondary: {
          DEFAULT: '#2563eb',
          dark: '#1e4ed8'
        },
        accent: {
          DEFAULT: '#facc15',
          dark: '#eab308'
        },
        neutral: '#64748b',
        dark: '#0f172a',
        light: '#f8fafc'
      },
      fontFamily: {
        sans: ['Nunito', 'ui-sans-serif', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [typography],
}
