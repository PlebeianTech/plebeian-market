module.exports = {
  content: [
    "./src/lib/components/*.svelte",
    "./src/lib/components/settings/*.svelte",
    "./src/routes/*.svelte",
    "./src/routes/auctions/*.svelte",
    "./src/routes/campaigns/*.svelte",
    "./src/routes/stall/*.svelte",
  ],
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
