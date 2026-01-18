<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import EventCard from '$lib/components/EventCard.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import { Button } from '$lib/components/ui/button';
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

<div class="flex min-h-screen bg-background">
	<Sidebar />

	<main class="flex-1 overflow-auto">
		<div class="container mx-auto max-w-7xl px-6 py-8">
			<div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 class="text-3xl font-bold tracking-tight">Events</h1>
					<p class="text-muted-foreground">Monitor webhook events from GitHub.</p>
				</div>

				<div class="flex gap-2">
					<select
						class="h-10 rounded-lg border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
						bind:value={filterType}
						onchange={handleFilterChange}
					>
						<option value="">All types</option>
						{#each eventTypes as type (type)}
							<option value={type}>{type}</option>
						{/each}
					</select>

					<select
						class="h-10 rounded-lg border bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
						bind:value={filterStatus}
						onchange={handleFilterChange}
					>
						<option value="">All statuses</option>
						{#each statuses as status (status)}
							<option value={status}>{status}</option>
						{/each}
					</select>
				</div>
			</div>

			{#if loading}
				<div class="rounded-xl border bg-card">
					<div class="divide-y">
						{#each [1, 2, 3, 4, 5] as idx (idx)}
							<div class="flex animate-pulse items-center gap-4 px-4 py-3">
								<div class="h-9 w-9 rounded-lg bg-muted"></div>
								<div class="flex-1">
									<div class="mb-2 h-4 w-32 rounded bg-muted"></div>
									<div class="h-3 w-24 rounded bg-muted"></div>
								</div>
								<div class="h-6 w-16 rounded-full bg-muted"></div>
							</div>
						{/each}
					</div>
				</div>
			{:else if error}
				<div
					class="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive"
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
						{error}
					</div>
				</div>
			{:else if events.length === 0}
				<EmptyState
					title="No events found"
					description={filterType || filterStatus
						? 'No events match the current filters. Try adjusting your filters.'
						: 'Events will appear here when webhooks are received from GitHub.'}
				/>
			{:else}
				<div class="rounded-xl border bg-card">
					<div class="divide-y">
						{#each events as event (event.id)}
							<EventCard {event} />
						{/each}
					</div>
				</div>

				<!-- Pagination -->
				{#if totalPages > 1}
					<div class="mt-8 flex items-center justify-center gap-2">
						<Button
							variant="outline"
							size="sm"
							disabled={currentPage === 1}
							onclick={() => loadEvents(currentPage - 1)}
						>
							Previous
						</Button>
						<span class="px-4 text-sm text-muted-foreground">
							Page {currentPage} of {totalPages}
						</span>
						<Button
							variant="outline"
							size="sm"
							disabled={currentPage === totalPages}
							onclick={() => loadEvents(currentPage + 1)}
						>
							Next
						</Button>
					</div>
				{/if}
			{/if}
		</div>
	</main>
</div>
