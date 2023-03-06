import { sveltekit } from '@sveltejs/kit/vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit'

/** @type {import('vite').UserConfig} */
const config = {
    plugins: [
        sveltekit(),
        SvelteKitPWA({
            devOptions: {
                enabled: true
            }
        })
    ]
};

export default config;
