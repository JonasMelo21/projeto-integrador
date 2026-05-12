import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: 'var(--primary, #030213)',
        'primary-foreground': 'var(--primary-foreground, #ffffff)',
        background: 'var(--background, #ffffff)',
        foreground: 'var(--foreground, #030213)',
        card: 'var(--card, #ffffff)',
        'card-foreground': 'var(--card-foreground, #030213)',
        secondary: 'var(--secondary, #f5f5f7)',
        'secondary-foreground': 'var(--secondary-foreground, #030213)',
        muted: 'var(--muted, #ececf0)',
        'muted-foreground': 'var(--muted-foreground, #717182)',
        border: 'var(--border, rgba(0, 0, 0, 0.1))',
        success: 'var(--success, #10b981)',
        'success-foreground': 'var(--success-foreground, #ffffff)',
        warning: 'var(--warning, #f59e0b)',
        'warning-foreground': 'var(--warning-foreground, #ffffff)',
        destructive: 'var(--destructive, #d4183d)',
      }
    }
  },
  plugins: [],
} satisfies Config
