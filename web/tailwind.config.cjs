module.exports = {
  content: ['./src/lib/components/*.svelte', './src/routes/*.svelte'],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          ...require("daisyui/src/colors/themes")["[data-theme=light]"],
          primary: "#aa00dd",
        },
      },
      {
        night: {
          ...require("daisyui/src/colors/themes")["[data-theme=night]"],
          primary: "#aa00dd",
        },
      }
    ],
    darkTheme: "night"
  },
}
