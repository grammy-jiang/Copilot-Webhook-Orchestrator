<script lang="ts">
	import type { Repository, Event } from '$lib/types';
	import RepositoryCard from './RepositoryCard.svelte';
	import EventCard from './EventCard.svelte';
	import { Button } from '$lib/components/ui/button';
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

	// Computed stats
	const stats = $derived([
		{
			label: 'Total Repositories',
			value: repositories.length.toString(),
			icon: 'repo',
			change: null
		},
		{
			label: 'Recent Events',
			value: recentEvents.length.toString(),
			icon: 'activity',
			change: null
		},
		{
			label: 'Processed Events',
			value: recentEvents.filter((e) => e.processed).length.toString(),
			icon: 'check',
			change: null
		},
		{
			label: 'Pending Events',
			value: recentEvents.filter((e) => !e.processed).length.toString(),
			icon: 'clock',
			change: null
		}
	]);
</script>

<div class="space-y-8" data-testid="dashboard">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">Dashboard</h1>
			<p class="text-muted-foreground">Monitor your Copilot workflow orchestration.</p>
		</div>
		<Button onclick={fetchDashboardData} disabled={isLoading} variant="outline">
			{#if isLoading}
				<svg
					class="mr-2 h-4 w-4 animate-spin"
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
				>
					<circle
						class="opacity-25"
						cx="12"
						cy="12"
						r="10"
						stroke="currentColor"
						stroke-width="4"
					></circle>
					<path
						class="opacity-75"
						fill="currentColor"
						d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
					></path>
				</svg>
				Refreshing...
			{:else}
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
					<path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
					<path d="M3 3v5h5" />
					<path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
					<path d="M16 16h5v5" />
				</svg>
				Refresh
			{/if}
		</Button>
	</div>

	{#if error}
		<div class="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
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
	{/if}

	{#if isLoading}
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
			{#each [1, 2, 3, 4] as idx (idx)}
				<div class="animate-pulse rounded-xl border bg-card p-6">
					<div class="mb-2 h-4 w-24 rounded bg-muted"></div>
					<div class="h-8 w-16 rounded bg-muted"></div>
				</div>
			{/each}
		</div>
	{:else}
		<!-- Stats Cards -->
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
			{#each stats as stat (stat.label)}
				<div class="rounded-xl border bg-card p-6 shadow-sm">
					<div class="flex items-center justify-between">
						<p class="text-sm font-medium text-muted-foreground">{stat.label}</p>
						{#if stat.icon === 'repo'}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
								class="h-4 w-4 text-muted-foreground"
							>
								<path
									d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.28 1.15-.28 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"
								/>
								<path d="M9 18c-4.51 2-5-2-7-2" />
							</svg>
						{:else if stat.icon === 'activity'}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
								class="h-4 w-4 text-muted-foreground"
							>
								<polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
							</svg>
						{:else if stat.icon === 'check'}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
								class="h-4 w-4 text-muted-foreground"
							>
								<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
								<polyline points="22 4 12 14.01 9 11.01" />
							</svg>
						{:else if stat.icon === 'clock'}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
								class="h-4 w-4 text-muted-foreground"
							>
								<circle cx="12" cy="12" r="10" />
								<polyline points="12 6 12 12 16 14" />
							</svg>
						{/if}
					</div>
					<p class="mt-2 text-3xl font-bold">{stat.value}</p>
				</div>
			{/each}
		</div>

		<!-- Repositories Section -->
		<section class="space-y-4">
			<div class="flex items-center justify-between">
				<h2 class="text-xl font-semibold">Repositories</h2>
				<a
					href="/repositories"
					class="inline-flex items-center text-sm font-medium text-primary hover:underline"
				>
					View all
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="ml-1 h-4 w-4"
					>
						<path d="M5 12h14" />
						<path d="m12 5 7 7-7 7" />
					</svg>
				</a>
			</div>

			{#if repositories.length === 0}
				<div class="rounded-xl border border-dashed bg-card p-8 text-center">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="mx-auto h-12 w-12 text-muted-foreground/50"
					>
						<path
							d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.28 1.15-.28 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"
						/>
						<path d="M9 18c-4.51 2-5-2-7-2" />
					</svg>
					<p class="mt-4 text-muted-foreground">No repositories connected.</p>
				</div>
			{:else}
				<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
					{#each repositories.slice(0, 6) as repository (repository.id)}
						<RepositoryCard {repository} />
					{/each}
				</div>
			{/if}
		</section>

		<!-- Recent Events Section -->
		<section class="space-y-4">
			<div class="flex items-center justify-between">
				<h2 class="text-xl font-semibold">Recent Events</h2>
				<a
					href="/events"
					class="inline-flex items-center text-sm font-medium text-primary hover:underline"
				>
					View all
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="ml-1 h-4 w-4"
					>
						<path d="M5 12h14" />
						<path d="m12 5 7 7-7 7" />
					</svg>
				</a>
			</div>

			{#if recentEvents.length === 0}
				<div class="rounded-xl border border-dashed bg-card p-8 text-center">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="mx-auto h-12 w-12 text-muted-foreground/50"
					>
						<polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
					</svg>
					<p class="mt-4 text-muted-foreground">No events received yet.</p>
				</div>
			{:else}
				<div class="rounded-xl border bg-card">
					<div class="divide-y">
						{#each recentEvents as event (event.id)}
							<EventCard {event} />
						{/each}
					</div>
				</div>
			{/if}
		</section>
	{/if}
</div>
