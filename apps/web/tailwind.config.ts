import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          green: "#00ed64",
          "green-deep": "#00b545",
          "green-pressed": "#008c34",
          "green-dark": "#00684a",
          "green-mid": "#00a35c",
          "green-soft": "#c3f0d2",
          "teal-deep": "#001e2b",
          teal: "#003d4f",
          "teal-mid": "#00684a",
        },
        surface: {
          DEFAULT: "#f9fbfa",
          soft: "#f4f7f6",
          feature: "#e3fcef",
        },
        hairline: {
          DEFAULT: "#e1e5e8",
          soft: "#eceff1",
          strong: "#c1ccd6",
          dark: "#1c2d38",
        },
        ink: "#001e2b",
        charcoal: "#1c2d38",
        slate: "#3d4f5b",
        steel: "#5c6c7a",
        stone: "#7c8c9a",
        muted: "#a8b3bc",
        canvas: {
          DEFAULT: "#ffffff",
          dark: "#001e2b",
        },
        accent: {
          purple: "#7b3ff2",
          orange: "#fa6e39",
          pink: "#f06bb8",
          blue: "#3d4f9f",
        },
      },
      borderRadius: {
        xs: "4px",
        sm: "6px",
        md: "8px",
        lg: "12px",
        xl: "16px",
        xxl: "24px",
        full: "9999px",
      },
      fontFamily: {
        sans: [
          "Euclid Circular A",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "Source Code Pro",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "monospace",
        ],
      },
      boxShadow: {
        card: "0 2px 6px rgba(0, 30, 43, 0.06), 0 1px 3px rgba(0, 30, 43, 0.04)",
        "card-hover": "0 8px 24px rgba(0, 30, 43, 0.10)",
        popover: "0 10px 30px rgba(0, 30, 43, 0.16)",
      },
    },
  },
  plugins: [],
} satisfies Config;
