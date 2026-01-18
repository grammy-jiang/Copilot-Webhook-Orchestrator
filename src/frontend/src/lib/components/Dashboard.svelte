<script lang="ts">
	import type { Repository, Event } from '$lib/types';
	import RepositoryCard from './RepositoryCard.svelte';
	import EventCard from './EventCard.svelte';
	import { onMount } from 'svelte';

	let repositories = $state<Repository[]>([]);
	let recentEvents = $state<Event[]>([]);
	let isLoading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		await fetchDashboardData();
	});

	async function fetchDashboardData() {
		isLoading = true;
		error = null;

		try {
			const [reposResponse, eventsResponse] = await Promise.all([
				fetch('/api/installations/repositories'),
				fetch('/api/events?limit=10')
			]);

			if (reposResponse.ok) {
				const reposData = await reposResponse.json();
				repositories = reposData.items ?? [];
			}

			if (eventsResponse.ok) {
				const eventsData = await eventsResponse.json();
				recentEvents = eventsData.items ?? [];
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load dashboard data';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="space-y-8" data-testid="dashboard">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">Dashboard</h1>
			<p class="text-muted-foreground">Monitor your Copilot workflow orchestration.</p>
		</div>
		<button
			onclick={fetchDashboardData}
			class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
			disabled={isLoading}
		>
			{isLoading ? 'Refreshing...' : 'Refresh'}
		</button>
	</div>

	{#if error}
		<div class="rounded-md border border-destructive/50 bg-destructive/10 p-4 text-destructive">
			{error}
		</div>
	{/if}

	{#if isLoading}
		<div class="flex h-64 items-center justify-center">
			<div class="text-muted-foreground">Loading dashboard...</div>
		</div>
	{:else}
		<!-- Repositories Grid -->
		<section>
			<div class="mb-4 flex items-center justify-between">
				<h2 class="text-xl font-semibold">Repositories</h2>
				<a href="/repositories" class="text-sm text-primary hover:underline">View all →</a>
			</div>

			{#if repositories.length === 0}
				<div class="rounded-lg border border-dashed p-8 text-center">
					<p class="text-muted-foreground">No repositories connected.</p>
				</div>
			{:else}
				<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
					{#each repositories.slice(0, 6) as repository (repository.id)}
						<RepositoryCard {repository} />
					{/each}
				</div>
			{/if}
		</section>

		<!-- Recent Events -->
		<section>
			<div class="mb-4 flex items-center justify-between">
				<h2 class="text-xl font-semibold">Recent Events</h2>
				<a href="/events" class="text-sm text-primary hover:underline">View all →</a>
			</div>

			{#if recentEvents.length === 0}
				<div class="rounded-lg border border-dashed p-8 text-center">
					<p class="text-muted-foreground">No events received yet.</p>
				</div>
			{:else}
				<div class="space-y-2">
					{#each recentEvents as event (event.id)}
						<EventCard {event} />
					{/each}
				</div>
			{/if}
		</section>
	{/if}
</div>
