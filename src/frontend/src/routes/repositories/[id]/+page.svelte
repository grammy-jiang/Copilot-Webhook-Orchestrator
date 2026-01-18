<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import EventCard from '$lib/components/EventCard.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import { Button } from '$lib/components/ui/button';
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

<div class="flex min-h-screen bg-background">
	<Sidebar />

	<main class="flex-1 overflow-auto">
		<div class="container mx-auto max-w-7xl px-6 py-8">
			{#if loading}
				<div class="animate-pulse space-y-6">
					<div class="h-4 w-32 rounded bg-muted"></div>
					<div class="h-8 w-64 rounded bg-muted"></div>
					<div class="grid gap-4 sm:grid-cols-2">
						<div class="h-24 rounded-xl bg-muted"></div>
						<div class="h-24 rounded-xl bg-muted"></div>
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
						<a href="/repositories" class="ml-2 underline">Back to repositories</a>
					</div>
				</div>
			{:else if repository}
				<!-- Back link -->
				<a
					href="/repositories"
					class="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
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
						<path d="m15 18-6-6 6-6" />
					</svg>
					Back to repositories
				</a>

				<!-- Repository Header -->
				<div class="mb-8 mt-4">
					<div class="flex items-start justify-between gap-4">
						<div class="flex items-center gap-4">
							<div
								class="flex h-12 w-12 items-center justify-center rounded-xl bg-muted"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
									class="h-6 w-6 text-muted-foreground"
								>
									<path
										d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.28 1.15-.28 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"
									/>
									<path d="M9 18c-4.51 2-5-2-7-2" />
								</svg>
							</div>
							<div>
								<h1 class="text-3xl font-bold tracking-tight">
									{repository.full_name}
								</h1>
								<p class="text-muted-foreground">
									Default branch: {repository.default_branch}
								</p>
							</div>
						</div>
						<div class="flex items-center gap-2">
							{#if repository.private}
								<span
									class="inline-flex items-center gap-1 rounded-md bg-muted px-2.5 py-1 text-xs text-muted-foreground"
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
										class="h-3 w-3"
									>
										<rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
										<path d="M7 11V7a5 5 0 0 1 10 0v4" />
									</svg>
									Private
								</span>
							{/if}
							<Button
								variant="outline"
								href="https://github.com/{repository.full_name}"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
									class="mr-2 h-4 w-4"
								>
									<path
										d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.28 1.15-.28 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"
									/>
									<path d="M9 18c-4.51 2-5-2-7-2" />
								</svg>
								View on GitHub
							</Button>
						</div>
					</div>
				</div>

				<!-- Stats -->
				<div class="mb-8 grid gap-4 sm:grid-cols-2">
					<div class="rounded-xl border bg-card p-6 shadow-sm">
						<div class="text-sm font-medium text-muted-foreground">Default Branch</div>
						<div class="mt-2 text-2xl font-bold">{repository.default_branch}</div>
					</div>
					<div class="rounded-xl border bg-card p-6 shadow-sm">
						<div class="text-sm font-medium text-muted-foreground">Last Updated</div>
						<div class="mt-2 text-2xl font-bold">
							{new Date(repository.updated_at).toLocaleDateString()}
						</div>
					</div>
				</div>

				<!-- Events -->
				<section class="space-y-4">
					<h2 class="text-xl font-semibold">Recent Events</h2>

					{#if events.length === 0}
						<EmptyState
							title="No events yet"
							description="Events will appear here when webhooks are received for this repository."
						/>
					{:else}
						<div class="rounded-xl border bg-card">
							<div class="divide-y">
								{#each events as event (event.id)}
									<EventCard {event} showRepository={false} />
								{/each}
							</div>
						</div>

						<!-- Pagination -->
						{#if totalPages > 1}
							<div class="mt-6 flex items-center justify-center gap-2">
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
				</section>
			{/if}
		</div>
	</main>
</div>
