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
        background: "#090A0F",
        surface: {
          DEFAULT: "#11131A",
          raised: "#161922",
          hover: "#1C202B",
          subtle: "#12151E",
        },
        border: {
          DEFAULT: "#1E222D",
          subtle: "#161A24",
          strong: "#2A2F3D",
          glow: "#383E4E",
        },
        brand: {
          orange: "#FF5F00",
          red: "#EB001B",
          gold: "#F79E1B",
        },
        threat: {
          low: "#10B981",
          medium: "#F59E0B",
          high: "#EF4444",
          critical: "#DC2626",
        },
        telemetry: {
          cyan: "#0284C7",
          blue: "#3B82F6",
          purple: "#7C3AED",
          slate: "#94A3B8",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};
