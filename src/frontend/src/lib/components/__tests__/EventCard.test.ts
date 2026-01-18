import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import EventCard from '../EventCard.svelte';
import type { Event } from '$lib/types';

describe('EventCard', () => {
	const baseEvent: Event = {
		id: 'event-1',
		delivery_id: 'delivery-123',
		event_type: 'pull_request',
		event_action: 'opened',
		repository_id: 'repo-1',
		repository_name: 'testowner/testrepo',
		actor: 'testuser',
		processing_status: 'processed',
		created_at: '2024-01-15T10:30:00Z',
		github_timestamp: '2024-01-15T10:29:00Z'
	};

	it('renders event type and action', () => {
		render(EventCard, { props: { event: baseEvent } });
		expect(screen.getByText('pull_request: opened')).toBeInTheDocument();
	});

	it('renders processing status', () => {
		render(EventCard, { props: { event: baseEvent } });
		expect(screen.getByText('processed')).toBeInTheDocument();
	});

	it('renders repository name when showRepository is true', () => {
		render(EventCard, { props: { event: baseEvent, showRepository: true } });
		expect(screen.getByText('testowner/testrepo')).toBeInTheDocument();
	});

	it('does not render repository name when showRepository is false', () => {
		render(EventCard, { props: { event: baseEvent, showRepository: false } });
		expect(screen.queryByText('testowner/testrepo')).not.toBeInTheDocument();
	});

	it('renders actor name', () => {
		render(EventCard, { props: { event: baseEvent } });
		expect(screen.getByText('@testuser')).toBeInTheDocument();
	});

	it('links to event detail page', () => {
		render(EventCard, { props: { event: baseEvent } });
		const link = screen.getByRole('link', { name: 'Details →' });
		expect(link).toHaveAttribute('href', '/events/event-1');
	});

	it('shows appropriate status styling for different statuses', () => {
		const receivedEvent = { ...baseEvent, processing_status: 'received' as const };
		render(EventCard, { props: { event: receivedEvent } });
		expect(screen.getByText('received')).toBeInTheDocument();
	});

	it('shows failed status correctly', () => {
		const failedEvent = { ...baseEvent, processing_status: 'failed' as const };
		render(EventCard, { props: { event: failedEvent } });
		expect(screen.getByText('failed')).toBeInTheDocument();
	});

	it('has correct test id', () => {
		render(EventCard, { props: { event: baseEvent } });
		expect(screen.getByTestId('event-card')).toBeInTheDocument();
	});
});
