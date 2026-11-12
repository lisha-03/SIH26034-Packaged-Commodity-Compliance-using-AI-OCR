/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#0b1523",
          900: "#0f1f33",
          800: "#152a45",
          700: "#1d3a5f",
        },
      },
    },
  },
  plugins: [],
}
