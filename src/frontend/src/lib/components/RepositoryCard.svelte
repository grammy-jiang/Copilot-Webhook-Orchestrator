<script lang="ts">
	import type { Repository, HealthStatus } from '$lib/types';

	interface Props {
		repository: Repository;
	}

	let { repository }: Props = $props();

	// Calculate health status based on updated_at time (since we don't have last_event_at)
	function getHealthStatus(): HealthStatus {
		if (!repository.updated_at) return 'healthy'; // No activity data, assume healthy
		const lastUpdate = new Date(repository.updated_at);
		if (isNaN(lastUpdate.getTime())) return 'healthy'; // Invalid date, assume healthy
		const now = new Date();
		const hoursSinceUpdate = (now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60);

		if (hoursSinceUpdate < 1) return 'healthy';
		if (hoursSinceUpdate < 24) return 'warning';
		return 'error';
	}

	function formatTimeAgo(dateString: string | null | undefined): string {
		if (!dateString) return 'No activity';
		const date = new Date(dateString);
		if (isNaN(date.getTime())) return 'No activity';
		const now = new Date();
		const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

		if (seconds < 0) return 'Just now'; // Future date edge case
		if (seconds < 60) return 'Just now';
		if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
		if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
		return `${Math.floor(seconds / 86400)}d ago`;
	}

	const healthStatus = $derived(getHealthStatus());
	const healthColors = {
		healthy: 'bg-green-500',
		warning: 'bg-yellow-500',
		error: 'bg-red-500'
	};
</script>

<a
	href="/repositories/{repository.id}"
	class="block rounded-xl border bg-card p-5 shadow-sm transition-all hover:border-primary/20 hover:shadow-md"
	data-testid="repository-card"
>
	<div class="flex items-start justify-between gap-3">
		<div class="flex min-w-0 items-center gap-3">
			<div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					class="h-5 w-5 text-muted-foreground"
				>
					<path
						d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.28 1.15-.28 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"
					/>
					<path d="M9 18c-4.51 2-5-2-7-2" />
				</svg>
			</div>
			<div class="min-w-0">
				<h3 class="truncate font-semibold text-card-foreground">{repository.full_name}</h3>
				<div class="mt-1 flex items-center gap-2">
					<span class="h-2 w-2 rounded-full {healthColors[healthStatus]}"></span>
					<span class="text-xs capitalize text-muted-foreground">{healthStatus}</span>
				</div>
			</div>
		</div>
		{#if repository.private}
			<span
				class="inline-flex shrink-0 items-center gap-1 rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground"
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
	</div>

	<div class="mt-4 flex items-center justify-between text-sm text-muted-foreground">
		<div class="flex items-center gap-2">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="h-3.5 w-3.5"
			>
				<line x1="6" y1="3" x2="6" y2="15" />
				<circle cx="18" cy="6" r="3" />
				<circle cx="6" cy="18" r="3" />
				<path d="M18 9a9 9 0 0 1-9 9" />
			</svg>
			<span>{repository.default_branch}</span>
		</div>
		<div class="flex items-center gap-1">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="h-3.5 w-3.5"
			>
				<circle cx="12" cy="12" r="10" />
				<polyline points="12 6 12 12 16 14" />
			</svg>
			<span>{formatTimeAgo(repository.updated_at)}</span>
		</div>
	</div>
</a>
