/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary": "#D4AF37", // Brand Gold
                "primary-hover": "#b5952f",
                "accent-blue": "#1754cf",
                "logic-gold": "#D4AF37",
                "logic-gold-dim": "#63521a",
                "background-light": "#f6f6f8",
                "background-dark": "#0f1115",
                "surface-dark": "#181b21",
                "surface-darker": "#0f1115",
                "surface-lighter": "#1A1D24",
                "surface-light": "#1A1D24",
                "border-dark": "#2A2F3A",
                "signal-bullish": "#ff3333",
                "signal-bearish": "#00e676",
                "signal-neutral": "#94a3b8",
                "market-up": "#ff4d4d",
                "market-down": "#00e676",
                "panic-dark": "#1f2937",
                "panic-teal": "#115e59",
                "depression-gray": "#64748b",
                "optimism-red": "#f87171",
                "extreme-red": "#991b1b",
                "gold": {
                    50: "#FBF8EB",
                    100: "#F6EFD3",
                    200: "#EBDBA3",
                    300: "#E0C773",
                    400: "#D4AF37",
                    500: "#B5952F",
                    600: "#967B27",
                    700: "#77611F",
                    800: "#584717",
                    900: "#3D320F",
                }
            },
            fontFamily: {
                "sans": ["Inter", "PingFang SC", "Noto Sans SC", "system-ui", "-apple-system", "sans-serif"],
                "display": ["Inter", "PingFang SC", "Noto Sans SC", "sans-serif"],
                "body": ["Inter", "PingFang SC", "Noto Sans SC", "sans-serif"],
                "mono": ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"]
            },
            borderRadius: {
                "DEFAULT": "0.25rem",
                "lg": "0.5rem",
                "xl": "0.75rem",
                "2xl": "1rem",
                "full": "9999px"
            },
            boxShadow: {
                "glow": "0 0 20px rgba(23, 84, 207, 0.3)",
                "glow-gold": "0 0 15px rgba(212, 175, 55, 0.2)",
                "glow-primary": "0 0 15px rgba(212, 175, 55, 0.2)",
                "glow-red": "0 0 20px rgba(255, 77, 77, 0.25)",
                "glow-green": "0 0 20px rgba(0, 230, 118, 0.25)",
            },
            backgroundImage: {
                "grid-pattern": "linear-gradient(to right, #1f2937 1px, transparent 1px), linear-gradient(to bottom, #1f2937 1px, transparent 1px)",
            }
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/container-queries'),
    ],
}
