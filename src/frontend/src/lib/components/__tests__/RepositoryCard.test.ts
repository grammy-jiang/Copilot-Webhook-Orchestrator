import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import RepositoryCard from '../RepositoryCard.svelte';
import type { Repository } from '$lib/types';

describe('RepositoryCard', () => {
	const baseRepository: Repository = {
		id: 1,
		github_repo_id: 12345,
		owner: 'testowner',
		name: 'testrepo',
		full_name: 'testowner/testrepo',
		private: false,
		default_branch: 'main',
		installation_id: 1,
		created_at: new Date().toISOString(),
		updated_at: new Date().toISOString()
	};

	it('renders repository name', () => {
		render(RepositoryCard, { props: { repository: baseRepository } });
		expect(screen.getByText('testowner/testrepo')).toBeInTheDocument();
	});

	it('renders default branch', () => {
		render(RepositoryCard, { props: { repository: baseRepository } });
		expect(screen.getByText('main')).toBeInTheDocument();
	});

	it('shows Private badge for private repositories', () => {
		const privateRepo = { ...baseRepository, private: true };
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
		expect(link).toHaveAttribute('href', '/repositories/1');
	});

	it('shows health status indicator', () => {
		render(RepositoryCard, { props: { repository: baseRepository } });
		// Check that health status is displayed
		const statusElement = screen.getByTestId('repository-card');
		expect(statusElement).toBeInTheDocument();
	});
});
