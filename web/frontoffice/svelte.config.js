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
			'$sharedLib': '../shared/lib',
		},
		prerender: {
			entries: [
				'*',
				'/p/[pubkey]',
				'/p/[pubkey]/stall/[stallId]'
			],
			handleHttpError: ({ path, referrer, message }) => {
				if (path === '/admin') {
					return;
				}

				// otherwise fail the build
				throw new Error(message);
			}
		},
		paths: {
			base: ''
		}
	},
	preprocess: sveltePreprocess()
};

export default config;
