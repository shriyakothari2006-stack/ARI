/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ari: {
          bg: '#FFF8FC',
          blush: '#F4DCEB',
          'blush-light': '#FDF2F8',
          lavender: '#E8DDF8',
          'lavender-light': '#F4EDFC',
          mauve: '#9C648F',
          'mauve-dark': '#79476C',
          text: '#302938',
          secondary: '#807485',
          border: '#EED9E8',
          surface: '#FFFFFF',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Playfair Display', 'Georgia', 'serif'],
      },
      boxShadow: {
        glass: '0 8px 32px 0 rgba(156, 100, 143, 0.08)',
        'glass-hover': '0 12px 40px 0 rgba(156, 100, 143, 0.16)',
        subtle: '0 2px 10px rgba(48, 41, 56, 0.04)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        float: 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
    },
  },
  plugins: [],
};
