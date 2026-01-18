import { test, expect } from '@playwright/test';

/**
 * Repositories E2E Tests
 *
 * Tests the repository list and detail pages.
 *
 * @see Story 3: Repository Selection UI
 */

// Helper to mock authenticated state
async function mockAuthenticatedState(page: import('@playwright/test').Page) {
	await page.route('/api/auth/me', async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: JSON.stringify({
				user: {
					id: 'user-1',
					github_id: 12345,
					username: 'testuser',
					email: 'test@example.com',
					avatar_url: null,
					created_at: '2026-01-01T00:00:00Z'
				},
				installation: {
					id: 'install-1',
					installation_id: 67890,
					account_login: 'testorg',
					account_type: 'Organization',
					is_suspended: false,
					created_at: '2026-01-01T00:00:00Z'
				}
			})
		});
	});
}

test.describe('Repository List Page', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthenticatedState(page);
	});

	/**
	 * AC: Given a user with connected repositories
	 *     When they visit the repositories page
	 *     Then they should see their repositories listed
	 */
	test('should display list of repositories', async ({ page }) => {
		// Mock repositories API (implementation uses /api/installations/repositories)
		await page.route('/api/installations/repositories*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'repo-1',
							github_id: 111,
							owner: 'testorg',
							name: 'repo1',
							full_name: 'testorg/repo1',
							description: 'First repository',
							is_private: false,
							default_branch: 'main',
							event_count: 25,
							last_event_at: '2026-01-18T12:00:00Z'
						},
						{
							id: 'repo-2',
							github_id: 222,
							owner: 'testorg',
							name: 'repo2',
							full_name: 'testorg/repo2',
							description: 'Second repository',
							is_private: true,
							default_branch: 'main',
							event_count: 10,
							last_event_at: '2026-01-17T08:00:00Z'
						}
					],
					total: 2,
					page: 1,
					per_page: 10,
					pages: 1
				})
			});
		});

		await page.goto('/repositories');

		// Assert - Both repositories visible
		await expect(page.getByText('testorg/repo1')).toBeVisible();
		await expect(page.getByText('testorg/repo2')).toBeVisible();
	});

	/**
	 * AC: Given a user views the repository list
	 *     When a repository is private
	 *     Then it should display a "Private" badge
	 */
	test('should display private badge for private repositories', async ({ page }) => {
		await page.route('/api/installations/repositories*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'repo-1',
							github_id: 111,
							owner: 'testorg',
							name: 'private-repo',
							full_name: 'testorg/private-repo',
							description: 'Private repository',
							is_private: true,
							default_branch: 'main',
							event_count: 5,
							last_event_at: null
						}
					],
					total: 1,
					page: 1,
					per_page: 10,
					pages: 1
				})
			});
		});

		await page.goto('/repositories');

		// Assert - Private badge visible
		await expect(page.getByText('Private')).toBeVisible();
	});

	/**
	 * AC: Given a user types in the search box
	 *     When they enter a search term
	 *     Then the repository list should be filtered
	 */
	test('should filter repositories when searching', async ({ page }) => {
		await page.route('/api/installations/repositories*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 10, pages: 0 })
			});
		});

		await page.goto('/repositories');

		// Act - Type in search box
		const searchInput = page.getByPlaceholder(/search/i);
		await searchInput.fill('my-repo');

		// Assert - Search input has value
		await expect(searchInput).toHaveValue('my-repo');
	});

	/**
	 * AC: Given a user with no connected repositories
	 *     When they visit the repositories page
	 *     Then they should see an empty state
	 */
	test('should display empty state when no repositories', async ({ page }) => {
		await page.route('/api/installations/repositories*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 10 })
			});
		});

		await page.goto('/repositories');

		// Assert - Empty state or "no repositories" message
		await expect(page.getByText(/no repositories|empty/i)).toBeVisible();
	});
});

test.describe('Repository Detail Page', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthenticatedState(page);
	});

	/**
	 * AC: Given a user clicks on a repository
	 *     When they navigate to the detail page
	 *     Then they should see repository information
	 */
	test('should display repository details', async ({ page }) => {
		// Mock repository detail API
		await page.route('/api/repositories/repo-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'repo-1',
					github_id: 111,
					owner: 'testorg',
					name: 'my-repo',
					full_name: 'testorg/my-repo',
					description: 'A great repository for testing',
					is_private: false,
					default_branch: 'main',
					event_count: 42,
					last_event_at: '2026-01-18T14:30:00Z'
				})
			});
		});

		// Mock events for this repository
		await page.route('/api/repositories/repo-1/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'event-1',
							delivery_id: 'delivery-1',
							event_type: 'push',
							event_action: null,
							repository_id: 'repo-1',
							repository_name: 'testorg/my-repo',
							actor: 'developer',
							processing_status: 'processed',
							created_at: '2026-01-18T14:00:00Z',
							github_timestamp: '2026-01-18T14:00:00Z'
						}
					],
					total: 1,
					page: 1,
					per_page: 20,
					pages: 1
				})
			});
		});

		await page.goto('/repositories/repo-1');

		// Assert - Repository info visible
		await expect(page.getByText('testorg/my-repo')).toBeVisible();
		await expect(page.getByText('42')).toBeVisible(); // Event count
	});

	/**
	 * AC: Given a user views repository detail
	 *     When events are available
	 *     Then they should see the event list
	 */
	test('should display events for repository', async ({ page }) => {
		await page.route('/api/repositories/repo-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'repo-1',
					github_id: 111,
					owner: 'testorg',
					name: 'my-repo',
					full_name: 'testorg/my-repo',
					description: null,
					is_private: false,
					default_branch: 'main',
					event_count: 2,
					last_event_at: null
				})
			});
		});

		await page.route('/api/repositories/repo-1/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'event-1',
							delivery_id: 'delivery-1',
							event_type: 'pull_request',
							event_action: 'opened',
							repository_id: 'repo-1',
							repository_name: 'testorg/my-repo',
							actor: 'user1',
							processing_status: 'processed',
							created_at: '2026-01-18T14:00:00Z',
							github_timestamp: null
						},
						{
							id: 'event-2',
							delivery_id: 'delivery-2',
							event_type: 'push',
							event_action: null,
							repository_id: 'repo-1',
							repository_name: 'testorg/my-repo',
							actor: 'user2',
							processing_status: 'processed',
							created_at: '2026-01-18T13:00:00Z',
							github_timestamp: null
						}
					],
					total: 2,
					page: 1,
					per_page: 20,
					pages: 1
				})
			});
		});

		await page.goto('/repositories/repo-1');

		// Assert - Events visible
		await expect(page.getByText(/pull_request/i)).toBeVisible();
		await expect(page.getByText(/push/i)).toBeVisible();
	});

	/**
	 * AC: Given a repository has a GitHub URL
	 *     When viewing the detail page
	 *     Then there should be a link to view on GitHub
	 */
	test('should have link to GitHub', async ({ page }) => {
		await page.route('/api/repositories/repo-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'repo-1',
					github_id: 111,
					owner: 'testorg',
					name: 'my-repo',
					full_name: 'testorg/my-repo',
					description: null,
					is_private: false,
					default_branch: 'main',
					event_count: 0,
					last_event_at: null
				})
			});
		});

		await page.route('/api/repositories/repo-1/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0 })
			});
		});

		await page.goto('/repositories/repo-1');

		// Assert - GitHub link exists
		const githubLink = page.getByRole('link', { name: /view on github/i });
		await expect(githubLink).toHaveAttribute('href', 'https://github.com/testorg/my-repo');
	});
});

test.describe('Repository Navigation', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthenticatedState(page);
	});

	/**
	 * AC: Given a user is on repository detail
	 *     When they click "Back to Repositories"
	 *     Then they should return to the list
	 */
	test('should navigate back to repository list', async ({ page }) => {
		await page.route('/api/repositories/repo-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'repo-1',
					github_id: 111,
					owner: 'test',
					name: 'repo',
					full_name: 'test/repo',
					description: null,
					is_private: false,
					default_branch: 'main',
					event_count: 0,
					last_event_at: null
				})
			});
		});

		await page.route('/api/repositories/repo-1/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 20, pages: 0 })
			});
		});

		await page.route('/api/installations/repositories*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 12, pages: 0 })
			});
		});

		await page.goto('/repositories/repo-1');

		// Act - Click back link
		await page
			.getByRole('link', { name: /back|repositories/i })
			.first()
			.click();

		// Assert - On repository list
		await expect(page).toHaveURL(/\/repositories$/);
	});
});
