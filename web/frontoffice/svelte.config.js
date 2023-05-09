import adapter from '@sveltejs/adapter-static';
import sveltePreprocess from 'svelte-preprocess';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			//out: 'build'
			// default options are shown. On some platforms
			// these options are set automatically — see below
			pages: 'build',
			assets: 'build',
			fallback: null,
			precompress: false,
			strict: true
		}),
		alias: {
			// this will match a directory and its contents
			// (`my-directory/x` resolves to `path/to/my-directory/x`)
			'$sharedLib': '../src/lib',
			'$sharedLibComponents': '../src/lib/components',
		},
		prerender: {
			entries: [
				'*',
				'/p/[pubkey]',
				'/p/[pubkey]/stall/[stallId]'
			]
		}
	},
	preprocess: sveltePreprocess()
};

export default config;
