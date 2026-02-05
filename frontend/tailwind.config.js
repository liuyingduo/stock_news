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
                "primary": "#1754cf", // Geek Blue
                "primary-hover": "#1448b3",
                "logic-gold": "#D4AF37", // Logic Gold
                "background-light": "#f6f6f8",
                "background-dark": "#0B0E11", // Deep dark
                "surface-dark": "#151921",
                "border-dark": "#2A2F3A"
            },
            fontFamily: {
                "sans": ["Inter", "PingFang SC", "Noto Sans SC", "system-ui", "-apple-system", "sans-serif"],
                "mono": ["JetBrains Mono", "SF Mono", "Menlo", "Consolas", "monospace"]
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
            }
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/container-queries'),
    ],
}
