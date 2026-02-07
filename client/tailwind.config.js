/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Core backgrounds
                background: "#0a0a0a",
                surface: "#171717",
                "surface-light": "#1f1f1f",
                "surface-elevated": "#262626",

                // Primary brand colors
                primary: {
                    DEFAULT: "#3b82f6",
                    50: "#eff6ff",
                    100: "#dbeafe",
                    200: "#bfdbfe",
                    300: "#93c5fd",
                    400: "#60a5fa",
                    500: "#3b82f6",
                    600: "#2563eb",
                    700: "#1d4ed8",
                    800: "#1e40af",
                    900: "#1e3a8a",
                },

                // Semantic colors
                success: {
                    DEFAULT: "#10b981",
                    50: "#ecfdf5",
                    100: "#d1fae5",
                    500: "#10b981",
                    600: "#059669",
                },
                warning: {
                    DEFAULT: "#f59e0b",
                    50: "#fffbeb",
                    100: "#fef3c7",
                    500: "#f59e0b",
                    600: "#d97706",
                },
                danger: {
                    DEFAULT: "#ef4444",
                    50: "#fef2f2",
                    100: "#fee2e2",
                    500: "#ef4444",
                    600: "#dc2626",
                },
                info: {
                    DEFAULT: "#06b6d4",
                    50: "#ecfeff",
                    100: "#cffafe",
                    500: "#06b6d4",
                    600: "#0891b2",
                },

                // Neutral text
                muted: "#737373",
                subtle: "#a3a3a3",
            },

            // Standardized border radius
            borderRadius: {
                DEFAULT: "12px",
                sm: "8px",
                md: "12px",
                lg: "16px",
                xl: "20px",
                "2xl": "24px",
            },

            // Standardized spacing
            spacing: {
                "4.5": "1.125rem",
                "18": "4.5rem",
                "22": "5.5rem",
            },

            // Box shadows
            boxShadow: {
                "glow-sm": "0 0 10px rgba(59, 130, 246, 0.1)",
                "glow-md": "0 0 20px rgba(59, 130, 246, 0.15)",
                "glow-lg": "0 0 30px rgba(59, 130, 246, 0.2)",
                "inner-glow": "inset 0 0 20px rgba(59, 130, 246, 0.1)",
            },

            // Animations
            animation: {
                "fade-in": "fadeIn 0.3s ease-out forwards",
                "slide-up": "slideUp 0.3s ease-out forwards",
                "slide-down": "slideDown 0.3s ease-out forwards",
                "scale-in": "scaleIn 0.2s ease-out forwards",
                "pulse-soft": "pulseSoft 2s ease-in-out infinite",
            },
            keyframes: {
                fadeIn: {
                    "0%": { opacity: "0" },
                    "100%": { opacity: "1" },
                },
                slideUp: {
                    "0%": { opacity: "0", transform: "translateY(10px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
                slideDown: {
                    "0%": { opacity: "0", transform: "translateY(-10px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
                scaleIn: {
                    "0%": { opacity: "0", transform: "scale(0.95)" },
                    "100%": { opacity: "1", transform: "scale(1)" },
                },
                pulseSoft: {
                    "0%, 100%": { opacity: "1" },
                    "50%": { opacity: "0.7" },
                },
            },

            // Typography
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
