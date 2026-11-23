/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#0B1120',
          card: '#1E293B',
          border: '#334155',
          primary: '#0284C7',
          accent: '#F59E0B',
          danger: '#EF4444',
          success: '#10B981',
          warning: '#F97316'
        }
      }
    },
  },
  plugins: [],
}
