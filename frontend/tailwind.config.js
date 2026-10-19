/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Steep Editorial Monochrome & Warm Accent Tokens
        steep: {
          ink: "#17191c",
          paper: "#ffffff",
          mist: "#f2f2f3",
          fog: "#fafafb",
          slate: "#777b86",
          ash: "#979799",
          smoke: "#a3a6af",
          peach: "#fbe1d1",
          sienna: "#5d2a1a",
        },
        // Audyr Backward-Compatible Aliases
        audyr: {
          ink: "#17191c",
          "pure-paper": "#ffffff",
          "soft-mist": "#ededed",
          charcoal: "#17191c",
          ash: "#777b86",
          slate: "#777b86",
          muted: "#979799",
          fog: "#a3a6af",
          chalk: "#f2f2f3",
          "mint-whisper": "#ecfdf5",
          peach: "#fbe1d1",
          sienna: "#5d2a1a",
        },
        // Brand Identity (SDD 3.6.2)
        brand: {
          blue: "#2563EB",
          "blue-hover": "#1D4ED8",
          dark: "#17191c",
        },
        // Semantic Plagiarism Tiers
        tier: {
          lexical: "#EF4444",       // Merah Tier 1: Verbatim match
          "lexical-bg": "#FEF2F2",  // Merah Muda BG Tier 1
          semantic: "#F97316",      // Oranye Tier 2: Paraphrase match
          "semantic-bg": "#FFF7ED", // Oranye Muda BG Tier 2
          ai: "#EAB308",            // Kuning Tier 3: AI / Stylometric pattern
          "ai-bg": "#FEFCE8",       // Kuning Muda BG Tier 3
        },
        // Composite Severity Score Colors
        severity: {
          safe: "#22C55E",      // 0 - 25% Hijau
          warning: "#EAB308",   // 26 - 50% Kuning
          danger: "#F97316",    // 51 - 75% Oranye
          critical: "#EF4444",  // 76 - 100% Merah
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', '-apple-system', 'sans-serif'],
        serif: ['"Source Serif 4"', 'Georgia', 'ui-serif', 'serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      letterSpacing: {
        tight: "-0.025em",
        tighter: "-0.035em",
        wide: "0.025em",
      },
      borderRadius: {
        "steep-card": "24px",
        "steep-small": "16px",
        "steep-elevated": "20px",
        "steep-pill": "9999px",
        "audyr-card": "24px",
        "audyr-panel": "24px",
        "audyr-button": "9999px",
        "audyr-input": "16px",
        "audyr-image": "12px",
      },
      boxShadow: {
        "steep-artifact": "0 0 0 1px rgba(4,23,43,0.05), 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)",
        "steep-subtle": "oklab(0 0 0 / 0.05) 0px 0px 0px 1px, rgba(0, 0, 0, 0.08) 0px 4px 24px 0px",
        "audyr-subtle": "0 0 0 1px rgba(4,23,43,0.05), 0 20px 25px -5px rgba(0,0,0,0.06)",
        "audyr-subtle-2": "rgba(0, 0, 0, 0.05) 0px 1px 2px 0px",
        "audyr-button": "none",
        "audyr-panel": "0 0 0 1px rgba(4,23,43,0.05), 0 20px 25px -5px rgba(0,0,0,0.1)",
      },
    },
  },
  plugins: [],
}
