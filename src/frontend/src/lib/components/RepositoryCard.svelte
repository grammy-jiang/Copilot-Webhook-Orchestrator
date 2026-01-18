<script lang="ts">
	import type { Repository, HealthStatus } from '$lib/types';

	interface Props {
		repository: Repository;
	}

	let { repository }: Props = $props();

	// Calculate health status based on last event time
	function getHealthStatus(): HealthStatus {
		if (!repository.last_event_at) return 'warning';

		const lastEvent = new Date(repository.last_event_at);
		const now = new Date();
		const hoursSinceLastEvent = (now.getTime() - lastEvent.getTime()) / (1000 * 60 * 60);

		if (hoursSinceLastEvent < 1) return 'healthy';
		if (hoursSinceLastEvent < 24) return 'warning';
		return 'error';
	}

	function formatTimeAgo(dateString: string | null): string {
		if (!dateString) return 'Never';

		const date = new Date(dateString);
		const now = new Date();
		const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

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
	class="block rounded-lg border bg-card p-4 transition-shadow hover:shadow-md"
	data-testid="repository-card"
>
	<div class="flex items-start justify-between">
		<div class="flex-1 truncate">
			<div class="flex items-center gap-2">
				<span class="h-2 w-2 rounded-full {healthColors[healthStatus]}"></span>
				<h3 class="truncate font-medium text-card-foreground">{repository.full_name}</h3>
			</div>
			{#if repository.description}
				<p class="mt-1 truncate text-sm text-muted-foreground">{repository.description}</p>
			{/if}
		</div>
		{#if repository.is_private}
			<span class="ml-2 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
				Private
			</span>
		{/if}
	</div>

	<div class="mt-4 flex items-center justify-between text-sm text-muted-foreground">
		<div class="flex items-center gap-4">
			<span title="Total events">{repository.event_count} events</span>
		</div>
		<span title="Last event">
			{formatTimeAgo(repository.last_event_at)}
		</span>
	</div>
</a>
