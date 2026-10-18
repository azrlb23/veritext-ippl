/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Audyr Editorial Monochrome Tokens
        audyr: {
          ink: "#262626",
          "pure-paper": "#ffffff",
          "soft-mist": "#ededed",
          charcoal: "#171717",
          ash: "#686868",
          slate: "#515151",
          muted: "#737373",
          fog: "#929292",
          chalk: "#cbcbcb",
          "mint-whisper": "#ecfdf5",
        },
        // Brand Identity (SDD 3.6.2)
        brand: {
          blue: "#2563EB",
          "blue-hover": "#1D4ED8",
          dark: "#0F172A",
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
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      letterSpacing: {
        tight: "-0.025em",
        tighter: "-0.035em",
      },
      borderRadius: {
        "audyr-card": "14px",
        "audyr-panel": "18px",
        "audyr-button": "4px",
        "audyr-input": "4px",
        "audyr-image": "8px",
      },
      boxShadow: {
        "audyr-subtle": "rgba(0, 0, 0, 0.04) 0px 1px 3px 0px",
        "audyr-subtle-2": "rgba(0, 0, 0, 0.05) 0px 1px 2px 0px",
        "audyr-button": "inset 0 1px 0 rgba(255, 255, 255, 0.16), 0 1px 2px rgba(0, 0, 0, 0.24)",
        "audyr-panel": "rgba(0, 0, 0, 0.08) 0px 25px 50px -12px",
      },
    },
  },
  plugins: [],
}
