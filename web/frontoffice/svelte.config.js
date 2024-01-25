import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: '404.html',
			precompress: false,
			strict: true
		}),
		alias: {
			'$sharedLib': '../shared/src/lib',
		},
		prerender: {
			entries: [
				'*',
				'/p/[pubkey]',
				'/p/[pubkey]/stall/[stallId]',
				'/product/[product_id]',
				'/[...slug]'
			]
		},
		paths: {
			base: ''
		}
	},
	preprocess: vitePreprocess(),
};

export default config;
