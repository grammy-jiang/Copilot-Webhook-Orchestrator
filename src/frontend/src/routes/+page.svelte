<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Dashboard from '$lib/components/Dashboard.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';

	onMount(() => {
		if (!authStore.isAuthenticated) {
			goto('/login');
		}
	});
</script>

{#if authStore.isAuthenticated}
	<div class="flex min-h-screen bg-background">
		<Sidebar />
		<main class="flex-1 overflow-auto">
			<div class="container mx-auto max-w-7xl px-6 py-8">
				{#if authStore.hasInstallation}
					<Dashboard />
				{:else}
					<EmptyState
						title="No repositories connected"
						description="Install the GitHub App to start monitoring your Copilot workflows."
						actionLabel="Import Repository"
						actionHref="/api/installations/callback"
					/>
				{/if}
			</div>
		</main>
	</div>
{/if}
