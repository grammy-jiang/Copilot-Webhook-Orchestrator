<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { Button } from '$lib/components/ui/button';

	let errorMessage = $state('');
	let successMessage = $state('');

	onMount(() => {
		// Check for error or success messages in URL params
		const error = page.url.searchParams.get('error');
		const logout = page.url.searchParams.get('logout');

		if (error === 'session_expired') {
			errorMessage = 'Session expired. Please login again.';
		} else if (error === 'unauthorized') {
			errorMessage = 'Authorization failed. Please try again.';
		} else if (error) {
			errorMessage = 'An error occurred. Please try again.';
		}

		if (logout === 'success') {
			successMessage = 'You have been logged out.';
		}

		// Redirect if already authenticated
		if (authStore.isAuthenticated) {
			goto('/');
		}
	});

	function handleLogin() {
		window.location.href = '/api/auth/login';
	}
</script>

<div class="flex min-h-svh flex-col items-center justify-center gap-6 bg-muted p-6 md:p-10">
	<div class="flex w-full max-w-sm flex-col gap-6">
		<!-- Logo -->
		<a href="/" class="flex items-center gap-2 self-center font-medium">
			<div
				class="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-primary-foreground"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					class="h-4 w-4"
				>
					<path
						d="M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3"
					/>
				</svg>
			</div>
			Copilot Orchestrator
		</a>

		<!-- Messages -->
		{#if errorMessage}
			<div
				class="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
				data-testid="error-message"
			>
				<div class="flex items-center gap-2">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="h-4 w-4"
					>
						<circle cx="12" cy="12" r="10" />
						<line x1="12" y1="8" x2="12" y2="12" />
						<line x1="12" y1="16" x2="12.01" y2="16" />
					</svg>
					{errorMessage}
				</div>
			</div>
		{/if}

		{#if successMessage}
			<div
				class="rounded-lg border border-green-500/50 bg-green-500/10 px-4 py-3 text-sm text-green-700 dark:text-green-400"
				data-testid="success-message"
			>
				<div class="flex items-center gap-2">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="h-4 w-4"
					>
						<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
						<polyline points="22 4 12 14.01 9 11.01" />
					</svg>
					{successMessage}
				</div>
			</div>
		{/if}

		<!-- Login Card -->
		<div class="flex flex-col gap-6 rounded-xl border bg-card p-6 shadow-sm">
			<div class="flex flex-col items-center gap-2 text-center">
				<h1 class="text-2xl font-bold">Welcome back</h1>
				<p class="text-balance text-sm text-muted-foreground">
					Sign in with your GitHub account to continue
				</p>
			</div>

			<div class="grid gap-4">
				<Button onclick={handleLogin} class="w-full" data-testid="login-button">
					<svg class="mr-2 h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
						<path
							d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"
						/>
					</svg>
					Login with GitHub
				</Button>

				<div
					class="relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t after:border-border"
				>
					<span class="relative z-10 bg-card px-2 text-muted-foreground">
						Secure authentication
					</span>
				</div>
			</div>

			<div class="grid gap-3 text-center text-xs text-muted-foreground">
				<div class="flex items-center justify-center gap-2">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="h-3.5 w-3.5"
					>
						<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
						<path d="m9 12 2 2 4-4" />
					</svg>
					OAuth 2.0 with GitHub
				</div>
				<div class="flex items-center justify-center gap-2">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="h-3.5 w-3.5"
					>
						<rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
						<path d="M7 11V7a5 5 0 0 1 10 0v4" />
					</svg>
					No password stored
				</div>
			</div>
		</div>

		<div class="text-balance text-center text-xs text-muted-foreground">
			By signing in, you agree to the
			<a href="/terms" class="underline underline-offset-4 hover:text-primary"
				>Terms of Service</a
			>
			and
			<a href="/privacy" class="underline underline-offset-4 hover:text-primary"
				>Privacy Policy</a
			>.
		</div>
	</div>
</div>
