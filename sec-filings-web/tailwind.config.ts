import type { Config } from "tailwindcss";
import { fontFamily } from "tailwindcss/defaultTheme";
import typography from "@tailwindcss/typography";

export default {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "rgb(var(--background) / <alpha-value>)",
        foreground: "rgb(var(--foreground) / <alpha-value>)",
        primary: {
          DEFAULT: "rgb(var(--primary) / <alpha-value>)",
          foreground: "rgb(var(--primary-foreground) / <alpha-value>)",
        },
        secondary: {
          DEFAULT: "rgb(var(--secondary) / <alpha-value>)",
          foreground: "rgb(var(--secondary-foreground) / <alpha-value>)",
        },
        muted: {
          DEFAULT: "rgb(var(--muted) / <alpha-value>)",
          foreground: "rgb(var(--muted-foreground) / <alpha-value>)",
        },
        accent: {
          DEFAULT: "rgb(var(--accent) / <alpha-value>)",
          foreground: "rgb(var(--accent-foreground) / <alpha-value>)",
        },
        card: {
          DEFAULT: "rgb(var(--card) / <alpha-value>)",
          foreground: "rgb(var(--card-foreground) / <alpha-value>)",
        },
        border: "rgb(var(--border) / <alpha-value>)",
        ring: "rgb(var(--ring) / <alpha-value>)",
        success: "rgb(var(--success) / <alpha-value>)",
        danger: "rgb(var(--danger) / <alpha-value>)",
        warning: "rgb(var(--warning) / <alpha-value>)",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", ...fontFamily.sans],
        mono: ["var(--font-geist-mono)", ...fontFamily.mono],
      },
      boxShadow: {
        card: "var(--shadow-card)",
      },
      typography: {
        DEFAULT: {
          css: [
            {
              '--tw-prose-body': 'rgb(var(--foreground) / 0.92)',
              '--tw-prose-headings': 'rgb(var(--foreground))',
              '--tw-prose-lead': 'rgb(var(--muted-foreground))',
              '--tw-prose-links': 'rgb(var(--primary))',
              '--tw-prose-bold': 'rgb(var(--foreground))',
              '--tw-prose-counters': 'rgb(var(--muted-foreground))',
              '--tw-prose-bullets': 'rgb(var(--muted-foreground))',
              '--tw-prose-hr': 'rgb(var(--border))',
              '--tw-prose-quotes': 'rgb(var(--foreground))',
              '--tw-prose-quote-borders': 'rgb(var(--border))',
              '--tw-prose-captions': 'rgb(var(--muted-foreground))',
              '--tw-prose-code': 'rgb(var(--foreground))',
              '--tw-prose-pre-code': 'rgb(var(--foreground))',
              '--tw-prose-pre-bg': 'rgb(var(--muted))',
              '--tw-prose-th-borders': 'rgb(var(--border))',
              '--tw-prose-td-borders': 'rgb(var(--border))',
            },
          ],
        },
      },
    },
  },
  plugins: [typography],
} satisfies Config;
