import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true
			}
		}
	},
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		environment: 'jsdom',
		globals: true,
		setupFiles: ['./vitest.setup.ts'],
		// Ensure we use browser build of Svelte, not server
		alias: [{ find: /^svelte$/, replacement: 'svelte' }],
		// Required for Svelte 5 component testing
		server: {
			deps: {
				inline: [/svelte/]
			}
		}
	},
	// Ensure browser conditions are used
	resolve: {
		conditions: ['browser']
	}
});
