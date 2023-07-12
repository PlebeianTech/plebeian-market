module.exports = {
  content: [
    "./src/lib/components/**/*.svelte",
    "./src/routes/**/*.svelte",
    "./../shared/src/lib/components/**/*.svelte"
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
    themes: ["light", "dark"],
    darkTheme: "dark",
  },
  darkMode: ['class', '[data-theme="dark"]'],
};
