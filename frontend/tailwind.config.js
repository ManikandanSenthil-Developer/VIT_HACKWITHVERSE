/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#090a0f',
        foreground: '#f3f4f6',
        card: {
          DEFAULT: '#11131f',
          foreground: '#f9fafb',
          border: 'rgba(255, 255, 255, 0.08)',
        },
        mats: {
          purple: {
            DEFAULT: '#8b5cf6',
            light: '#a78bfa',
            dark: '#6d28d9',
            glow: 'rgba(139, 92, 246, 0.35)',
          },
          orange: {
            DEFAULT: '#f97316',
            light: '#fb923c',
            dark: '#ea580c',
            glow: 'rgba(249, 115, 22, 0.35)',
          },
          dark: {
            950: '#07080c',
            900: '#0b0d14',
            850: '#10131d',
            800: '#161926',
            700: '#232738',
            600: '#32374d',
          }
        },
      },
      backgroundImage: {
        'radial-gradient': 'radial-gradient(circle at 50% 50%, var(--tw-gradient-stops))',
        'glass-gradient': 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)',
        'purple-orange': 'linear-gradient(135deg, #8b5cf6 0%, #f97316 100%)',
      },
      boxShadow: {
        'glow-purple': '0 0 25px -5px rgba(139, 92, 246, 0.4)',
        'glow-orange': '0 0 25px -5px rgba(249, 115, 22, 0.4)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
