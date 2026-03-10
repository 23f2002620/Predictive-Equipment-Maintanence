/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      fontFamily: {
        sans:    ['"Manrope"', 'system-ui', 'sans-serif'],
        display: ['"DM Serif Display"', 'serif'],
        mono:    ['"SF Mono"', '"Fira Code"', 'monospace'],
      },
    },
  },
  plugins: [],
}