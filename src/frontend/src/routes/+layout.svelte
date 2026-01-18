<script lang="ts">
	import '../app.css';
	import { authStore } from '$lib/stores/auth.svelte';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(async () => {
		await authStore.fetchUser();
	});
</script>

<svelte:head>
	<title>Copilot Workflow Orchestrator</title>
	<meta name="description" content="Webhook-driven automation for GitHub Copilot workflows" />
</svelte:head>

{#if authStore.isLoading}
	<div class="flex h-screen items-center justify-center">
		<div class="text-muted-foreground">Loading...</div>
	</div>
{:else}
	{@render children()}
{/if}
