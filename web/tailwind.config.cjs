module.exports = {
  content: ['./src/lib/components/*.svelte', './src/routes/*.svelte'],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ['light', 'night'],
    darkTheme: "night"
  },
}
