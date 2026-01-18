<script lang="ts">
	import { Button } from '../ui/button';

	type ButtonVariant = 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
	type ButtonSize = 'default' | 'sm' | 'lg' | 'icon';

	interface Props {
		text: string;
		variant?: ButtonVariant;
		size?: ButtonSize;
		disabled?: boolean;
	}

	let { text, variant = 'default', size = 'default', disabled = false }: Props = $props();
</script>

<Button {variant} {size} {disabled}>{text}</Button>
