import svelte from 'rollup-plugin-svelte';
import resolve from 'rollup-plugin-node-resolve';
import commonjs from 'rollup-plugin-commonjs';
import livereload from 'rollup-plugin-livereload';
import { terser } from 'rollup-plugin-terser';

const production = !process.env.ROLLUP_WATCH;

const defs = [
	{
		input: 'src/buyer/main.js',
		output: {
			sourcemap: false,
			format: 'iife',
			name: 'PlebeianBuyer',
			file: 'app/buyer/bundle.js'
		},
	},
	{
		input: 'src/seller/main.js',
		output: {
			sourcemap: false,
			format: 'iife',
			name: 'PlebeianSeller',
			file: 'app/seller/bundle.js'
		},
	},
];

export default Array.from(defs,
	(def) => {
		return Object.assign(def,
			{
				plugins: [
					svelte({
						emitCss: false,
						compilerOptions: {
							// enable run-time checks when not in production
							dev: !production,
						}
					}),
			
					// If you have external dependencies installed from
					// npm, you'll most likely need these plugins. In
					// some cases you'll need additional configuration —
					// consult the documentation for details:
					// https://github.com/rollup/rollup-plugin-commonjs
					resolve({
						browser: true,
						dedupe: importee => importee === 'svelte' || importee.startsWith('svelte/')
					}),
					commonjs(),
			
					// Watch the `public` directory and refresh the
					// browser on changes when not in production
					!production && livereload('public'),
			
					// If we're building for production (npm run build
					// instead of npm run dev), minify
					production && terser()
				],
				watch: {
					clearScreen: false
				}
			});
	}
);