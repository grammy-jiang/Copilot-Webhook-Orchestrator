<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import Header from '$lib/components/Header.svelte';
	import RepositoryCard from '$lib/components/RepositoryCard.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import type { Repository, PaginatedResponse } from '$lib/types';

	let repositories = $state<Repository[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let currentPage = $state(1);
	let totalPages = $state(1);
	let searchQuery = $state('');

	onMount(async () => {
		if (!authStore.isAuthenticated) {
			goto('/login');
			return;
		}
		await loadRepositories();
	});

	async function loadRepositories(page = 1) {
		loading = true;
		error = null;
		try {
			const params = new URLSearchParams({
				page: page.toString(),
				per_page: '12'
			});
			if (searchQuery) {
				params.set('search', searchQuery);
			}

			const response = await fetch(`/api/installations/repositories?${params}`);
			if (!response.ok) throw new Error('Failed to load repositories');

			const data: PaginatedResponse<Repository> = await response.json();
			repositories = data.items;
			currentPage = data.page;
			totalPages = data.pages;
		} catch (e) {
			error = e instanceof Error ? e.message : 'An error occurred';
		} finally {
			loading = false;
		}
	}

	function handleSearch(event: Event) {
		const target = event.target as HTMLInputElement;
		searchQuery = target.value;
		loadRepositories(1);
	}
</script>

<svelte:head>
	<title>Repositories | Copilot Workflow Orchestrator</title>
</svelte:head>

<div class="min-h-screen bg-background">
	<Header />

	<main class="container mx-auto px-4 py-8">
		<div class="mb-6 flex items-center justify-between">
			<h1 class="text-2xl font-bold text-foreground">Repositories</h1>
			<input
				type="search"
				placeholder="Search repositories..."
				class="rounded-md border bg-background px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
				value={searchQuery}
				oninput={handleSearch}
			/>
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
		{:else if repositories.length === 0}
			<EmptyState
				title="No repositories found"
				description={searchQuery
					? 'No repositories match your search. Try a different query.'
					: 'No repositories connected yet. Install the GitHub App to connect repositories.'}
			/>
		{:else}
			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#each repositories as repository (repository.id)}
					<RepositoryCard {repository} />
				{/each}
			</div>

			<!-- Pagination -->
			{#if totalPages > 1}
				<div class="mt-8 flex items-center justify-center gap-2">
					<button
						class="rounded-md border px-3 py-2 text-sm disabled:opacity-50"
						disabled={currentPage === 1}
						onclick={() => loadRepositories(currentPage - 1)}
					>
						Previous
					</button>
					<span class="text-sm text-muted-foreground">
						Page {currentPage} of {totalPages}
					</span>
					<button
						class="rounded-md border px-3 py-2 text-sm disabled:opacity-50"
						disabled={currentPage === totalPages}
						onclick={() => loadRepositories(currentPage + 1)}
					>
						Next
					</button>
				</div>
			{/if}
		{/if}
	</main>
</div>
