<script lang="ts">
	import * as Empty from '$lib/components/ui/empty';
	import { Button } from '$lib/components/ui/button';

	interface Props {
		title: string;
		description: string;
		actionLabel?: string;
		actionHref?: string;
	}

	let { title, description, actionLabel, actionHref }: Props = $props();

	function handleAction() {
		if (actionHref) {
			window.location.href = actionHref;
		}
	}
</script>

<Empty.Root class="flex-1" data-testid="empty-state">
	<Empty.Header>
		<Empty.Media variant="icon">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="h-6 w-6"
			>
				<path
					d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.28 1.15-.28 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"
				/>
				<path d="M9 18c-4.51 2-5-2-7-2" />
			</svg>
		</Empty.Media>
		<Empty.Title>{title}</Empty.Title>
		<Empty.Description>{description}</Empty.Description>
	</Empty.Header>
	{#if actionLabel && actionHref}
		<Empty.Content>
			<Button onclick={handleAction}>{actionLabel}</Button>
		</Empty.Content>
	{/if}
</Empty.Root>
