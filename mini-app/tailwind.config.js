/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tg: {
          bg: 'var(--tg-bg-color, #ffffff)',
          text: 'var(--tg-text-color, #000000)',
          hint: 'var(--tg-hint-color, #999999)',
          link: 'var(--tg-link-color, #2481cc)',
          button: 'var(--tg-button-color, #2481cc)',
          buttonText: 'var(--tg-button-text-color, #ffffff)',
          secondaryBg: 'var(--tg-secondary-bg-color, #f5f5f5)',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
