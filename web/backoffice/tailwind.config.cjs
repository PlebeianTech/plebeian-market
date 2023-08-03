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
      screens: {
        '3xl': '1800px',
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
