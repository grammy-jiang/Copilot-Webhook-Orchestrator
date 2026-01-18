import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import EmptyState from '../EmptyState.svelte';

describe('EmptyState', () => {
	it('renders title and description', () => {
		render(EmptyState, {
			props: {
				title: 'No items found',
				description: 'There are no items to display'
			}
		});

		expect(screen.getByText('No items found')).toBeInTheDocument();
		expect(screen.getByText('There are no items to display')).toBeInTheDocument();
	});

	it('renders action button when actionLabel and actionHref are provided', () => {
		render(EmptyState, {
			props: {
				title: 'Get started',
				description: 'Connect your first repository',
				actionLabel: 'Connect Repository',
				actionHref: '/repositories/connect'
			}
		});

		const actionButton = screen.getByRole('button', { name: 'Connect Repository' });
		expect(actionButton).toBeInTheDocument();
	});

	it('does not render action button when actionLabel is not provided', () => {
		render(EmptyState, {
			props: {
				title: 'Empty',
				description: 'Nothing here'
			}
		});

		expect(screen.queryByRole('button', { name: /connect/i })).not.toBeInTheDocument();
	});

	it('has correct test id', () => {
		render(EmptyState, {
			props: {
				title: 'Test',
				description: 'Test description'
			}
		});

		expect(screen.getByTestId('empty-state')).toBeInTheDocument();
	});
});
