<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import RepositoryCard from '$lib/components/RepositoryCard.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import { Button } from '$lib/components/ui/button';
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

<div class="flex min-h-screen bg-background">
	<Sidebar />

	<main class="flex-1 overflow-auto">
		<div class="container mx-auto max-w-7xl px-6 py-8">
			<div class="mb-6 flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold tracking-tight">Repositories</h1>
					<p class="text-muted-foreground">Manage your connected repositories.</p>
				</div>
				<div class="flex items-center gap-3">
					<div class="relative">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
							class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
						>
							<circle cx="11" cy="11" r="8" />
							<path d="m21 21-4.3-4.3" />
						</svg>
						<input
							type="search"
							placeholder="Search repositories..."
							class="h-10 w-64 rounded-lg border bg-background pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
							value={searchQuery}
							oninput={handleSearch}
						/>
					</div>
					<a
						href="/api/installations/connect"
						class="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-ring"
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
							<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
							<path d="M19 3v4" />
							<path d="M21 5h-4" />
						</svg>
						Manage Repositories
					</a>
				</div>
			</div>

			{#if loading}
				<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{#each [1, 2, 3, 4, 5, 6] as idx (idx)}
						<div class="animate-pulse rounded-xl border bg-card p-5">
							<div class="flex items-center gap-3">
								<div class="h-10 w-10 rounded-lg bg-muted"></div>
								<div class="flex-1">
									<div class="mb-2 h-4 w-32 rounded bg-muted"></div>
									<div class="h-3 w-16 rounded bg-muted"></div>
								</div>
							</div>
							<div class="mt-4 flex justify-between">
								<div class="h-3 w-16 rounded bg-muted"></div>
								<div class="h-3 w-12 rounded bg-muted"></div>
							</div>
						</div>
					{/each}
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
						<Button
							variant="outline"
							size="sm"
							disabled={currentPage === 1}
							onclick={() => loadRepositories(currentPage - 1)}
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
							onclick={() => loadRepositories(currentPage + 1)}
						>
							Next
						</Button>
					</div>
				{/if}
			{/if}
		</div>
	</main>
</div>
