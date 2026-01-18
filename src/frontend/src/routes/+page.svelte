<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Header from '$lib/components/Header.svelte';
	import Dashboard from '$lib/components/Dashboard.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';

	onMount(() => {
		if (!authStore.isAuthenticated) {
			goto('/login');
		}
	});
</script>

{#if authStore.isAuthenticated}
	<div class="min-h-screen bg-background">
		<Header />
		<main class="container mx-auto px-4 py-8">
			{#if authStore.hasInstallation}
				<Dashboard />
			{:else}
				<EmptyState
					title="No repositories connected"
					description="Install the GitHub App to start monitoring your Copilot workflows."
					actionLabel="Connect Repositories"
					actionHref="/api/installations/callback"
				/>
			{/if}
		</main>
	</div>
{/if}
