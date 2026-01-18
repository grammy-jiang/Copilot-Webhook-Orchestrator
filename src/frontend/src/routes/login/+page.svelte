<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import Button from '$lib/components/ui/button/Button.svelte';

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

<div class="flex min-h-screen flex-col items-center justify-center bg-background px-4">
	<div class="w-full max-w-md space-y-8">
		<!-- Logo and Title -->
		<div class="text-center">
			<h1 class="text-3xl font-bold tracking-tight text-foreground">
				Copilot Workflow Orchestrator
			</h1>
			<p class="mt-2 text-muted-foreground">
				Webhook-driven automation for GitHub Copilot workflows
			</p>
		</div>

		<!-- Messages -->
		{#if errorMessage}
			<div
				class="rounded-md border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive"
				data-testid="error-message"
			>
				{errorMessage}
			</div>
		{/if}

		{#if successMessage}
			<div
				class="rounded-md border border-green-500/50 bg-green-500/10 p-4 text-sm text-green-700 dark:text-green-400"
				data-testid="success-message"
			>
				{successMessage}
			</div>
		{/if}

		<!-- Login Card -->
		<div class="rounded-lg border bg-card p-6 shadow-sm">
			<div class="space-y-4">
				<div class="text-center">
					<h2 class="text-lg font-semibold text-card-foreground">Sign in to continue</h2>
					<p class="mt-1 text-sm text-muted-foreground">
						Use your GitHub account to access the orchestrator.
					</p>
				</div>

				<Button onclick={handleLogin} class="w-full" data-testid="login-button">
					<svg class="mr-2 h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
						<path
							d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"
						/>
					</svg>
					Login with GitHub
				</Button>
			</div>
		</div>

		<!-- Features -->
		<div class="grid gap-4 text-center text-sm text-muted-foreground">
			<div class="flex items-center justify-center gap-2">
				<span class="inline-block h-1.5 w-1.5 rounded-full bg-primary"></span>
				Monitor webhook events in real-time
			</div>
			<div class="flex items-center justify-center gap-2">
				<span class="inline-block h-1.5 w-1.5 rounded-full bg-primary"></span>
				Track Copilot workflow states
			</div>
			<div class="flex items-center justify-center gap-2">
				<span class="inline-block h-1.5 w-1.5 rounded-full bg-primary"></span>
				Manage repositories and installations
			</div>
		</div>
	</div>
</div>
