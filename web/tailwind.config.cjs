module.exports = {
  content: ['./src/lib/components/*.svelte', './src/routes/*.svelte'],
  theme: {
    extend: {
      colors: {
        'neon-pink': '#ff00ff',
      }
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ['light', 'night'],
    darkTheme: "night"
  },
}
