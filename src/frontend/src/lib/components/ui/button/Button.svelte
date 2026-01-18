<script lang="ts">
	import type { HTMLButtonAttributes } from 'svelte/elements';
	import { buttonVariants, type ButtonVariant, type ButtonSize } from './variants';

	interface Props extends HTMLButtonAttributes {
		variant?: ButtonVariant;
		size?: ButtonSize;
		class?: string;
	}

	let {
		variant = 'default',
		size = 'default',
		class: className = '',
		children,
		...restProps
	}: Props = $props();
</script>

<button class="{buttonVariants({ variant, size })} {className}" {...restProps}>
	{@render children?.()}
</button>
