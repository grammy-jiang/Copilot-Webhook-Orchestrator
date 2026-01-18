import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import RepositoryCard from '../RepositoryCard.svelte';
import type { Repository } from '$lib/types';

describe('RepositoryCard', () => {
	const baseRepository: Repository = {
		id: 'repo-1',
		github_id: 12345,
		owner: 'testowner',
		name: 'testrepo',
		full_name: 'testowner/testrepo',
		description: 'A test repository',
		is_private: false,
		default_branch: 'main',
		last_event_at: new Date().toISOString(),
		event_count: 42
	};

	it('renders repository name', () => {
		render(RepositoryCard, { props: { repository: baseRepository } });
		expect(screen.getByText('testowner/testrepo')).toBeInTheDocument();
	});

	it('renders repository description', () => {
		render(RepositoryCard, { props: { repository: baseRepository } });
		expect(screen.getByText('A test repository')).toBeInTheDocument();
	});

	it('renders event count', () => {
		render(RepositoryCard, { props: { repository: baseRepository } });
		expect(screen.getByText('42 events')).toBeInTheDocument();
	});

	it('shows Private badge for private repositories', () => {
		const privateRepo = { ...baseRepository, is_private: true };
		render(RepositoryCard, { props: { repository: privateRepo } });
		expect(screen.getByText('Private')).toBeInTheDocument();
	});

	it('does not show Private badge for public repositories', () => {
		render(RepositoryCard, { props: { repository: baseRepository } });
		expect(screen.queryByText('Private')).not.toBeInTheDocument();
	});

	it('links to repository detail page', () => {
		render(RepositoryCard, { props: { repository: baseRepository } });
		const link = screen.getByTestId('repository-card');
		expect(link).toHaveAttribute('href', '/repositories/repo-1');
	});

	it('shows Never for repositories with no events', () => {
		const noEventsRepo = { ...baseRepository, last_event_at: null };
		render(RepositoryCard, { props: { repository: noEventsRepo } });
		expect(screen.getByText('Never')).toBeInTheDocument();
	});
});
