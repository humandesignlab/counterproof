import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "var(--bg)",
        surface: "var(--surface)",
        line: "var(--border)",
        ink: {
          DEFAULT: "var(--text)",
          muted: "var(--text-muted)",
          faint: "var(--text-faint)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          hover: "var(--accent-hover)",
          fg: "var(--accent-fg)",
        },
        pass: {
          DEFAULT: "var(--status-pass)",
          bg: "var(--status-pass-bg)",
          line: "var(--status-pass-line)",
        },
        review: {
          DEFAULT: "var(--status-review)",
          bg: "var(--status-review-bg)",
          line: "var(--status-review-line)",
        },
        fail: {
          DEFAULT: "var(--status-fail)",
          bg: "var(--status-fail-bg)",
          line: "var(--status-fail-line)",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
