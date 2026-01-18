<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { authStore } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import type { Event } from '$lib/types';

	let event = $state<Event | null>(null);
	let payload = $state<unknown>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const eventId = $derived(page.params.id);

	onMount(async () => {
		if (!authStore.isAuthenticated) {
			goto('/login');
			return;
		}
		await loadEvent();
	});

	async function loadEvent() {
		loading = true;
		error = null;
		try {
			const response = await fetch(`/api/events/${eventId}`);
			if (!response.ok) throw new Error('Event not found');

			const data = await response.json();
			event = data.event;
			payload = data.payload;
		} catch (e) {
			error = e instanceof Error ? e.message : 'An error occurred';
		} finally {
			loading = false;
		}
	}

	// Status based on processed boolean
	const statusLabel = $derived(event?.processed ? 'processed' : 'pending');
	const statusColors = {
		pending: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
		processed: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
	};
</script>

<svelte:head>
	<title>Event Details | Copilot Workflow Orchestrator</title>
</svelte:head>

<div class="flex min-h-screen bg-background">
	<Sidebar />

	<main class="flex-1 overflow-auto">
		<div class="container mx-auto max-w-7xl px-6 py-8">
			{#if loading}
				<div class="animate-pulse space-y-6">
					<div class="h-4 w-32 rounded bg-muted"></div>
					<div class="h-8 w-64 rounded bg-muted"></div>
					<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
						<div class="h-20 rounded-xl bg-muted"></div>
						<div class="h-20 rounded-xl bg-muted"></div>
						<div class="h-20 rounded-xl bg-muted"></div>
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
						<a href="/events" class="ml-2 underline">Back to events</a>
					</div>
				</div>
			{:else if event}
				<!-- Back link -->
				<a
					href="/events"
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
					Back to events
				</a>

				<!-- Header -->
				<div class="mb-8 mt-4">
					<div class="flex items-center gap-3">
						<div
							class="flex h-12 w-12 items-center justify-center rounded-xl bg-muted text-xl"
						>
							{event.event_type === 'pull_request'
								? '🔀'
								: event.event_type === 'issues'
									? '📋'
									: event.event_type === 'push'
										? '📤'
										: event.event_type === 'check_suite'
											? '✅'
											: event.event_type === 'check_run'
												? '🔍'
												: event.event_type === 'issue_comment'
													? '💬'
													: event.event_type === 'pull_request_review'
														? '👀'
														: event.event_type === 'installation'
															? '🔧'
															: '📨'}
						</div>
						<div>
							<div class="flex items-center gap-3">
								<h1 class="text-3xl font-bold tracking-tight">
									{event.event_type}
								</h1>
								{#if event.action}
									<span class="text-2xl text-muted-foreground"
										>· {event.action}</span
									>
								{/if}
								<span
									class="rounded-full px-3 py-1 text-sm font-medium {statusColors[
										statusLabel
									]}"
								>
									{statusLabel}
								</span>
							</div>
							{#if event.repository_id}
								<a
									href="/repositories/{event.repository_id}"
									class="text-muted-foreground hover:text-foreground hover:underline"
								>
									Repository #{event.repository_id}
								</a>
							{/if}
						</div>
					</div>
				</div>

				<!-- Details Grid -->
				<div class="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
					<div class="rounded-xl border bg-card p-5 shadow-sm">
						<div class="text-sm font-medium text-muted-foreground">Event ID</div>
						<div class="mt-2 truncate font-mono text-sm" title={String(event.id)}>
							{event.id}
						</div>
					</div>
					<div class="rounded-xl border bg-card p-5 shadow-sm">
						<div class="text-sm font-medium text-muted-foreground">Delivery ID</div>
						<div class="mt-2 truncate font-mono text-sm" title={event.delivery_id}>
							{event.delivery_id}
						</div>
					</div>
					<div class="rounded-xl border bg-card p-5 shadow-sm">
						<div class="text-sm font-medium text-muted-foreground">Received At</div>
						<div class="mt-2 text-sm">
							{new Date(event.created_at).toLocaleString()}
						</div>
					</div>
				</div>

				<!-- Payload -->
				{#if payload}
					<section class="space-y-4">
						<h2 class="text-xl font-semibold">Event Payload</h2>
						<div class="rounded-xl border bg-card shadow-sm">
							<pre class="max-h-[600px] overflow-auto p-6 text-sm"><code
									class="text-foreground">{JSON.stringify(payload, null, 2)}</code
								></pre>
						</div>
					</section>
				{/if}
			{/if}
		</div>
	</main>
</div>
