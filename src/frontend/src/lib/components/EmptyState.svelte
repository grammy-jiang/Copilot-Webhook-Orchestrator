<script lang="ts">
	interface Props {
		title: string;
		description: string;
		actionLabel?: string;
		actionHref?: string;
	}

	let { title, description, actionLabel, actionHref }: Props = $props();
</script>

<div
	class="flex flex-col items-center justify-center rounded-lg border border-dashed p-12 text-center"
	data-testid="empty-state"
>
	<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-muted">
		<svg
			class="h-8 w-8 text-muted-foreground"
			fill="none"
			viewBox="0 0 24 24"
			stroke="currentColor"
		>
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
			/>
		</svg>
	</div>

	<h3 class="mt-4 text-lg font-semibold text-foreground">{title}</h3>
	<p class="mt-2 max-w-md text-sm text-muted-foreground">{description}</p>

	{#if actionLabel && actionHref}
		<a
			href={actionHref}
			class="mt-6 inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
		>
			{actionLabel}
		</a>
	{/if}
</div>
