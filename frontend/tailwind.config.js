/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./react.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#070A10',
          900: '#0B0F19',
          850: '#0F1523',
          800: '#141C2D',
          750: '#192338',
          700: '#202C45',
          600: '#2A3A59',
        },
        brand: {
          orange: '#FF5722',
          orangeDark: '#E64A19',
          orangeGlow: '#FF7043',
          red: '#EF4444',
          yellow: '#F59E0B',
          green: '#10B981',
          cyan: '#0EA5E9',
          purple: '#8B5CF6'
        }
      },
      boxShadow: {
        'glow-orange': '0 0 20px -3px rgba(255, 87, 34, 0.45)',
        'glow-red': '0 0 20px -3px rgba(239, 68, 68, 0.45)',
        'card': '0 4px 20px -2px rgba(0, 0, 0, 0.5)',
      }
    },
  },
  plugins: [],
}
