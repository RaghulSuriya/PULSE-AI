/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0A0D14",
        surface: "#121824",
        "surface-card": "#1A2234",
        "surface-border": "#2A364F",
        primary: {
          50: "#EEF2FF",
          500: "#6366F1",
          600: "#4F46E5",
          700: "#4338CA",
        },
        accent: {
          cyan: "#06B6D4",
          amber: "#F59E0B",
          emerald: "#10B981",
          rose: "#F43F5E",
          purple: "#8B5CF6"
        }
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"]
      }
    },
  },
  plugins: [],
};
