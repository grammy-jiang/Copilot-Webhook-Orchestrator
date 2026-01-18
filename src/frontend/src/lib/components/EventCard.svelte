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

	const statusColors = {
		received: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
		processing: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
		processed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
		failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
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

<div
	class="flex items-center gap-4 rounded-lg border bg-card p-3 transition-colors hover:bg-accent/50"
	data-testid="event-card"
>
	<!-- Icon -->
	<div class="flex h-10 w-10 items-center justify-center rounded-full bg-muted text-lg">
		{icon}
	</div>

	<!-- Content -->
	<div class="min-w-0 flex-1">
		<div class="flex items-center gap-2">
			<span class="font-medium text-card-foreground">
				{event.event_type}{event.event_action ? `: ${event.event_action}` : ''}
			</span>
			<span class="rounded-full px-2 py-0.5 text-xs {statusColors[event.processing_status]}">
				{event.processing_status}
			</span>
		</div>
		<div class="mt-0.5 flex items-center gap-2 text-sm text-muted-foreground">
			{#if showRepository}
				<span class="truncate">{event.repository_name}</span>
				<span>·</span>
			{/if}
			{#if event.actor}
				<span>@{event.actor}</span>
				<span>·</span>
			{/if}
			<span>{formatTime(event.created_at)}</span>
		</div>
	</div>

	<!-- Link to detail -->
	<a href="/events/{event.id}" class="text-sm text-primary hover:underline" title="View details">
		Details →
	</a>
</div>
