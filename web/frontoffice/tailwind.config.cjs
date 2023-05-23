module.exports = {
  content: [
    "./src/lib/components/*.svelte",
    "./src/lib/components/**/*.svelte",
    "./src/routes/**/*.svelte",
  ],
  theme: {
    extend: {
      colors: {
        "neon-pink": "#ff00ff",
      },
    },
  },
  plugins: [
      require("daisyui"),
      function ({ addVariant }) {
        addVariant(
            'supports-backdrop-blur',
            '@supports (backdrop-filter: blur(0)) or (-webkit-backdrop-filter: blur(0))',
        );
        addVariant('supports-scrollbars', '@supports selector(::-webkit-scrollbar)');
        addVariant('children', '& > *');
        addVariant('scrollbar', '&::-webkit-scrollbar');
        addVariant('scrollbar-track', '&::-webkit-scrollbar-track');
        addVariant('scrollbar-thumb', '&::-webkit-scrollbar-thumb');
      },
  ],
  daisyui: {
    themes: ["light", "halloween"],
    darkTheme: "halloween",
  },
};