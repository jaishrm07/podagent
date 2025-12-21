/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Space Grotesk'", "sans-serif"],
      },
      colors: {
        ink: "#0b1021",
        shell: "#f4f5fb",
        accent: {
          DEFAULT: "#0ea5e9",
          soft: "#cceafe",
        },
      },
      boxShadow: {
        panel: "0 20px 60px rgba(11,16,33,0.08)",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: 0, transform: "translateY(6px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
      animation: {
        fadeIn: "fadeIn 0.28s ease",
      },
    },
  },
  plugins: [],
}
