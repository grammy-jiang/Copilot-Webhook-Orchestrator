import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import EventCard from '../EventCard.svelte';
import type { Event } from '$lib/types';

describe('EventCard', () => {
	const baseEvent: Event = {
		id: 1,
		delivery_id: 'delivery-123',
		event_type: 'pull_request',
		action: 'opened',
		repository_id: 1,
		processed: true,
		created_at: '2024-01-15T10:30:00Z'
	};

	it('renders event type', () => {
		render(EventCard, { props: { event: baseEvent } });
		expect(screen.getByText('pull_request')).toBeInTheDocument();
	});

	it('renders event action', () => {
		render(EventCard, { props: { event: baseEvent } });
		expect(screen.getByText('opened')).toBeInTheDocument();
	});

	it('renders processed status', () => {
		render(EventCard, { props: { event: baseEvent } });
		expect(screen.getByText('processed')).toBeInTheDocument();
	});

	it('renders repository ID when showRepository is true', () => {
		render(EventCard, { props: { event: baseEvent, showRepository: true } });
		expect(screen.getByText(/Repository #1/)).toBeInTheDocument();
	});

	it('does not render repository ID when showRepository is false', () => {
		render(EventCard, { props: { event: baseEvent, showRepository: false } });
		expect(screen.queryByText(/Repository #1/)).not.toBeInTheDocument();
	});

	it('links to event detail page', () => {
		render(EventCard, { props: { event: baseEvent } });
		const link = screen.getByTestId('event-card');
		expect(link).toHaveAttribute('href', '/events/1');
	});

	it('shows pending status for unprocessed events', () => {
		const pendingEvent = { ...baseEvent, processed: false };
		render(EventCard, { props: { event: pendingEvent } });
		expect(screen.getByText('pending')).toBeInTheDocument();
	});

	it('has correct test id', () => {
		render(EventCard, { props: { event: baseEvent } });
		expect(screen.getByTestId('event-card')).toBeInTheDocument();
	});
});
