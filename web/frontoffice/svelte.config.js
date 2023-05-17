import adapter from '@sveltejs/adapter-static';
import sveltePreprocess from 'svelte-preprocess';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: null,
			precompress: false,
			strict: true
		}),
		alias: {
			// this will match a directory and its contents
			// (`my-directory/x` resolves to `path/to/my-directory/x`)
			'$sharedLib': '../shared/lib',
		},
		prerender: {
			entries: [
				'*',
				'/p/[pubkey]',
				'/p/[pubkey]/stall/[stallId]'
			]
		},
		paths: {
			base: ''
		}
	},
	preprocess: sveltePreprocess()
};

export default config;
