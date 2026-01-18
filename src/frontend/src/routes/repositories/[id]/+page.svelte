<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import Header from '$lib/components/Header.svelte';
	import EventCard from '$lib/components/EventCard.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import type { Repository, Event, PaginatedResponse } from '$lib/types';

	let repository = $state<Repository | null>(null);
	let events = $state<Event[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let currentPage = $state(1);
	let totalPages = $state(1);

	const repositoryId = $derived(page.params.id);

	onMount(async () => {
		if (!authStore.isAuthenticated) {
			goto('/login');
			return;
		}
		await loadRepository();
	});

	async function loadRepository() {
		loading = true;
		error = null;
		try {
			const [repoResponse, eventsResponse] = await Promise.all([
				fetch(`/api/repositories/${repositoryId}`),
				fetch(`/api/repositories/${repositoryId}/events?per_page=20`)
			]);

			if (!repoResponse.ok) throw new Error('Repository not found');
			if (!eventsResponse.ok) throw new Error('Failed to load events');

			repository = await repoResponse.json();
			const eventsData: PaginatedResponse<Event> = await eventsResponse.json();
			events = eventsData.items;
			currentPage = eventsData.page;
			totalPages = eventsData.pages;
		} catch (e) {
			error = e instanceof Error ? e.message : 'An error occurred';
		} finally {
			loading = false;
		}
	}

	async function loadEvents(eventPage = 1) {
		try {
			const response = await fetch(
				`/api/repositories/${repositoryId}/events?page=${eventPage}&per_page=20`
			);
			if (!response.ok) throw new Error('Failed to load events');

			const data: PaginatedResponse<Event> = await response.json();
			events = data.items;
			currentPage = data.page;
			totalPages = data.pages;
		} catch (e) {
			error = e instanceof Error ? e.message : 'An error occurred';
		}
	}
</script>

<svelte:head>
	<title>{repository?.full_name ?? 'Repository'} | Copilot Workflow Orchestrator</title>
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
				<a href="/repositories" class="ml-2 underline">Back to repositories</a>
			</div>
		{:else if repository}
			<!-- Repository Header -->
			<div class="mb-8">
				<a href="/repositories" class="text-sm text-muted-foreground hover:underline">
					← Back to repositories
				</a>
				<div class="mt-4 flex items-start justify-between">
					<div>
						<h1 class="text-2xl font-bold text-foreground">{repository.full_name}</h1>
						{#if repository.description}
							<p class="mt-1 text-muted-foreground">{repository.description}</p>
						{/if}
					</div>
					<div class="flex items-center gap-2">
						{#if repository.is_private}
							<span
								class="rounded-full bg-muted px-3 py-1 text-sm text-muted-foreground"
							>
								Private
							</span>
						{/if}
						<a
							href="https://github.com/{repository.full_name}"
							target="_blank"
							rel="noopener noreferrer"
							class="rounded-md border px-3 py-1 text-sm hover:bg-accent"
						>
							View on GitHub →
						</a>
					</div>
				</div>
			</div>

			<!-- Stats -->
			<div class="mb-8 grid gap-4 sm:grid-cols-3">
				<div class="rounded-lg border bg-card p-4">
					<div class="text-sm text-muted-foreground">Total Events</div>
					<div class="text-2xl font-bold text-foreground">{repository.event_count}</div>
				</div>
				<div class="rounded-lg border bg-card p-4">
					<div class="text-sm text-muted-foreground">Default Branch</div>
					<div class="text-2xl font-bold text-foreground">
						{repository.default_branch}
					</div>
				</div>
				<div class="rounded-lg border bg-card p-4">
					<div class="text-sm text-muted-foreground">Last Event</div>
					<div class="text-2xl font-bold text-foreground">
						{repository.last_event_at
							? new Date(repository.last_event_at).toLocaleDateString()
							: 'Never'}
					</div>
				</div>
			</div>

			<!-- Events -->
			<section>
				<h2 class="mb-4 text-lg font-semibold text-foreground">Recent Events</h2>

				{#if events.length === 0}
					<EmptyState
						title="No events yet"
						description="Events will appear here when webhooks are received for this repository."
					/>
				{:else}
					<div class="space-y-3">
						{#each events as event (event.id)}
							<EventCard {event} showRepository={false} />
						{/each}
					</div>

					<!-- Pagination -->
					{#if totalPages > 1}
						<div class="mt-6 flex items-center justify-center gap-2">
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
			</section>
		{/if}
	</main>
</div>
