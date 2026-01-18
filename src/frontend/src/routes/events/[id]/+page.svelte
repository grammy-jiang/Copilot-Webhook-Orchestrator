<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import Header from '$lib/components/Header.svelte';
	import type { Event } from '$lib/types';

	let event = $state<Event | null>(null);
	let payload = $state<unknown>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const eventId = $derived(page.params.id);

	onMount(async () => {
		if (!authStore.isAuthenticated) {
			goto('/login');
			return;
		}
		await loadEvent();
	});

	async function loadEvent() {
		loading = true;
		error = null;
		try {
			const response = await fetch(`/api/events/${eventId}`);
			if (!response.ok) throw new Error('Event not found');

			const data = await response.json();
			event = data.event;
			payload = data.payload;
		} catch (e) {
			error = e instanceof Error ? e.message : 'An error occurred';
		} finally {
			loading = false;
		}
	}

	const statusColors = {
		received: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
		processing: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
		processed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
		failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
	};
</script>

<svelte:head>
	<title>Event Details | Copilot Workflow Orchestrator</title>
</svelte:head>

<div class="min-h-screen bg-background">
	<Header />

	<main class="container mx-auto px-4 py-8">
		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div
					class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"
				></div>
			</div>
		{:else if error}
			<div
				class="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive"
			>
				{error}
				<a href="/events" class="ml-2 underline">Back to events</a>
			</div>
		{:else if event}
			<!-- Back link -->
			<a href="/events" class="text-sm text-muted-foreground hover:underline">
				← Back to events
			</a>

			<!-- Header -->
			<div class="mb-8 mt-4">
				<div class="flex items-center gap-3">
					<h1 class="text-2xl font-bold text-foreground">
						{event.event_type}{event.event_action ? `: ${event.event_action}` : ''}
					</h1>
					<span
						class="rounded-full px-3 py-1 text-sm {statusColors[
							event.processing_status
						]}"
					>
						{event.processing_status}
					</span>
				</div>
				<p class="mt-1 text-muted-foreground">
					<a
						href="/repositories/{event.repository_id}"
						class="hover:text-foreground hover:underline"
					>
						{event.repository_name}
					</a>
					{#if event.actor}
						• by @{event.actor}
					{/if}
				</p>
			</div>

			<!-- Details Grid -->
			<div class="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
				<div class="rounded-lg border bg-card p-4">
					<div class="text-sm text-muted-foreground">Event ID</div>
					<div class="mt-1 truncate font-mono text-sm text-foreground" title={event.id}>
						{event.id}
					</div>
				</div>
				<div class="rounded-lg border bg-card p-4">
					<div class="text-sm text-muted-foreground">Delivery ID</div>
					<div
						class="mt-1 truncate font-mono text-sm text-foreground"
						title={event.delivery_id}
					>
						{event.delivery_id}
					</div>
				</div>
				<div class="rounded-lg border bg-card p-4">
					<div class="text-sm text-muted-foreground">Received At</div>
					<div class="mt-1 text-sm text-foreground">
						{new Date(event.created_at).toLocaleString()}
					</div>
				</div>
				<div class="rounded-lg border bg-card p-4">
					<div class="text-sm text-muted-foreground">GitHub Timestamp</div>
					<div class="mt-1 text-sm text-foreground">
						{event.github_timestamp
							? new Date(event.github_timestamp).toLocaleString()
							: 'N/A'}
					</div>
				</div>
			</div>

			<!-- Payload -->
			{#if payload}
				<section>
					<h2 class="mb-4 text-lg font-semibold text-foreground">Event Payload</h2>
					<div class="rounded-lg border bg-card">
						<pre class="max-h-[600px] overflow-auto p-4 text-sm"><code
								class="text-foreground">{JSON.stringify(payload, null, 2)}</code
							></pre>
					</div>
				</section>
			{/if}
		{/if}
	</main>
</div>
