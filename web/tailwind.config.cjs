module.exports = {
  content: [
    "./src/lib/components/*.svelte",
    "./src/lib/components/settings/*.svelte",
    "./src/routes/**/*.svelte",
  ],
  theme: {
    extend: {
      colors: {
        "neon-pink": "#ff00ff",
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light", "halloween"],
    darkTheme: "halloween",
  },
};
