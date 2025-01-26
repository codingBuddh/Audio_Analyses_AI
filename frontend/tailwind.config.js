/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#f59e0b',  // Amber
        secondary: '#9ca3af', // Gray
        accent: '#fbbf24',   // Amber
        background: '#111827', // Darker gray
        surface: '#1f2937',   // Dark gray
        text: '#f3f4f6',      // Light gray
      },
      fontFamily: {
        lato: ['Lato', 'sans-serif'],
      },
      boxShadow: {
        'dashboard': '0 1px 3px rgba(0, 0, 0, 0.1)',
      },
      borderWidth: {
        '1': '1px',
      },
    },
  },
  plugins: [],
} 