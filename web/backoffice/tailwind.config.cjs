module.exports = {
  content: [
    "./src/lib/components/**/*.svelte",
    "./src/routes/**/*.svelte",
    "./../shared/lib/components/**/*.svelte",
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
