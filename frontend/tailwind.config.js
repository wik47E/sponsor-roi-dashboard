/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        body: ["'Work Sans'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      colors: {
        paper: "#f6f2e9",
        ink: {
          DEFAULT: "#1c1b29",
          soft: "#3d3b52",
          dim: "#5c596e",
        },
        gold: {
          DEFAULT: "#b8863f",
          light: "#d9b877",
        },
        panel: "#fffdf7",
        line: "#e2dbc9",
        verdict: {
          under: "#2f6b4f",
          fair: "#8a7f5c",
          over: "#a4402f",
        },
      },
    },
  },
  plugins: [],
};
