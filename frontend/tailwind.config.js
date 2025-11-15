export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        // Einstein-inspired medical color palette
        einstein: {
          blue: '#0066CC',      // Primary medical blue
          'blue-dark': '#004C99', // Darker blue for hover states
          'blue-light': '#E6F2FF', // Light blue background
          green: '#00A859',      // Medical green accent
          'green-light': '#E6F5ED', // Light green background
          gray: {
            50: '#FAFAFA',
            100: '#F5F5F5',
            200: '#E5E5E5',
            300: '#D4D4D4',
            400: '#A3A3A3',
            500: '#737373',
            600: '#525252',
            700: '#404040',
            800: '#262626',
            900: '#171717',
          }
        },
        primary: '#0066CC',
        secondary: '#00A859'
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', 'sans-serif'],
      },
    }
  },
  plugins: []
};

