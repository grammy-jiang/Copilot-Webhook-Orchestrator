<script lang="ts">
	import type { Event } from '$lib/types';

	interface Props {
		event: Event;
		showRepository?: boolean;
	}

	let { event, showRepository = true }: Props = $props();

	function formatTime(dateString: string): string {
		return new Date(dateString).toLocaleString();
	}

	function formatTimeAgo(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

		if (seconds < 60) return 'Just now';
		if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
		if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
		return `${Math.floor(seconds / 86400)}d ago`;
	}

	// Status based on processed boolean
	const statusLabel = $derived(event.processed ? 'processed' : 'pending');
	const statusColors = {
		pending: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
		processed: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
	};

	const eventTypeIcons: Record<string, string> = {
		pull_request: '🔀',
		issues: '📋',
		push: '📤',
		check_suite: '✅',
		check_run: '🔍',
		issue_comment: '💬',
		pull_request_review: '👀',
		installation: '🔧'
	};

	const icon = $derived(eventTypeIcons[event.event_type] ?? '📨');
</script>

<a
	href="/events/{event.id}"
	class="flex items-center gap-4 px-4 py-3 transition-colors hover:bg-accent/50"
	data-testid="event-card"
>
	<!-- Icon -->
	<div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-muted text-base">
		{icon}
	</div>

	<!-- Content -->
	<div class="min-w-0 flex-1">
		<div class="flex items-center gap-2">
			<span class="font-medium text-card-foreground">
				{event.event_type}
			</span>
			{#if event.action}
				<span class="text-muted-foreground">·</span>
				<span class="text-sm text-muted-foreground">{event.action}</span>
			{/if}
		</div>
		<div class="mt-0.5 flex items-center gap-2 text-xs text-muted-foreground">
			{#if showRepository && event.repository_id}
				<span class="truncate">Repository #{event.repository_id}</span>
				<span>·</span>
			{/if}
			<span title={formatTime(event.created_at)}>{formatTimeAgo(event.created_at)}</span>
		</div>
	</div>

	<!-- Status -->
	<span class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium {statusColors[statusLabel]}">
		{statusLabel}
	</span>

	<!-- Arrow -->
	<svg
		xmlns="http://www.w3.org/2000/svg"
		viewBox="0 0 24 24"
		fill="none"
		stroke="currentColor"
		stroke-width="2"
		stroke-linecap="round"
		stroke-linejoin="round"
		class="h-4 w-4 shrink-0 text-muted-foreground"
	>
		<path d="m9 18 6-6-6-6" />
	</svg>
</a>
