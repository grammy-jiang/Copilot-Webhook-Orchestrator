<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import Header from '$lib/components/Header.svelte';
	import EventCard from '$lib/components/EventCard.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import type { Event, PaginatedResponse } from '$lib/types';

	let events = $state<Event[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let currentPage = $state(1);
	let totalPages = $state(1);
	let filterType = $state('');
	let filterStatus = $state('');

	const eventTypes = [
		'pull_request',
		'issues',
		'push',
		'check_suite',
		'check_run',
		'issue_comment',
		'pull_request_review',
		'installation'
	];
	const statuses = ['received', 'processing', 'processed', 'failed'];

	onMount(async () => {
		if (!authStore.isAuthenticated) {
			goto('/login');
			return;
		}
		await loadEvents();
	});

	async function loadEvents(page = 1) {
		loading = true;
		error = null;
		try {
			const params = new URLSearchParams({
				page: page.toString(),
				per_page: '20'
			});
			if (filterType) params.set('event_type', filterType);
			if (filterStatus) params.set('status', filterStatus);

			const response = await fetch(`/api/events?${params}`);
			if (!response.ok) throw new Error('Failed to load events');

			const data: PaginatedResponse<Event> = await response.json();
			events = data.items;
			currentPage = data.page;
			totalPages = data.pages;
		} catch (e) {
			error = e instanceof Error ? e.message : 'An error occurred';
		} finally {
			loading = false;
		}
	}

	function handleFilterChange() {
		loadEvents(1);
	}
</script>

<svelte:head>
	<title>Events | Copilot Workflow Orchestrator</title>
</svelte:head>

<div class="min-h-screen bg-background">
	<Header />

	<main class="container mx-auto px-4 py-8">
		<div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<h1 class="text-2xl font-bold text-foreground">Events</h1>

			<div class="flex gap-2">
				<select
					class="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
					bind:value={filterType}
					onchange={handleFilterChange}
				>
					<option value="">All types</option>
					{#each eventTypes as type}
						<option value={type}>{type}</option>
					{/each}
				</select>

				<select
					class="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
					bind:value={filterStatus}
					onchange={handleFilterChange}
				>
					<option value="">All statuses</option>
					{#each statuses as status}
						<option value={status}>{status}</option>
					{/each}
				</select>
			</div>
		</div>

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
			</div>
		{:else if events.length === 0}
			<EmptyState
				title="No events found"
				description={filterType || filterStatus
					? 'No events match the current filters. Try adjusting your filters.'
					: 'Events will appear here when webhooks are received from GitHub.'}
			/>
		{:else}
			<div class="space-y-3">
				{#each events as event (event.id)}
					<EventCard {event} />
				{/each}
			</div>

			<!-- Pagination -->
			{#if totalPages > 1}
				<div class="mt-8 flex items-center justify-center gap-2">
					<button
						class="rounded-md border px-3 py-2 text-sm disabled:opacity-50"
						disabled={currentPage === 1}
						onclick={() => loadEvents(currentPage - 1)}
					>
						Previous
					</button>
					<span class="text-sm text-muted-foreground">
						Page {currentPage} of {totalPages}
					</span>
					<button
						class="rounded-md border px-3 py-2 text-sm disabled:opacity-50"
						disabled={currentPage === totalPages}
						onclick={() => loadEvents(currentPage + 1)}
					>
						Next
					</button>
				</div>
			{/if}
		{/if}
	</main>
</div>
