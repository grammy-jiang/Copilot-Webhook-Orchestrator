import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import ButtonTestWrapper from './ButtonTestWrapper.svelte';

describe('Button', () => {
	it('renders button with text', () => {
		render(ButtonTestWrapper, {
			props: {
				text: 'Click me'
			}
		});
		expect(screen.getByRole('button')).toBeInTheDocument();
	});

	it('applies default variant classes', () => {
		render(ButtonTestWrapper, {
			props: {
				text: 'Default'
			}
		});
		const button = screen.getByRole('button');
		expect(button).toHaveClass('bg-primary');
	});

	it('applies destructive variant classes', () => {
		render(ButtonTestWrapper, {
			props: {
				variant: 'destructive',
				text: 'Delete'
			}
		});
		const button = screen.getByRole('button');
		expect(button).toHaveClass('bg-destructive');
	});

	it('applies outline variant classes', () => {
		render(ButtonTestWrapper, {
			props: {
				variant: 'outline',
				text: 'Outline'
			}
		});
		const button = screen.getByRole('button');
		expect(button).toHaveClass('border');
	});

	it('applies size classes correctly', () => {
		render(ButtonTestWrapper, {
			props: {
				size: 'sm',
				text: 'Small'
			}
		});
		const button = screen.getByRole('button');
		expect(button).toHaveClass('h-9');
	});

	it('respects disabled attribute', () => {
		render(ButtonTestWrapper, {
			props: {
				disabled: true,
				text: 'Disabled'
			}
		});
		const button = screen.getByRole('button');
		expect(button).toBeDisabled();
	});
});
