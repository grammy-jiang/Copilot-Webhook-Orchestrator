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
				id: 'user-1',
				login: 'testuser',
				name: 'Test User'
			})
		});
	});

	await page.route('/api/installations', async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: JSON.stringify([{ id: 'install-1', account_login: 'testorg' }])
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
		// Mock repositories API
		await page.route('/api/repositories*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'repo-1',
							full_name: 'testorg/repo1',
							description: 'First repository',
							private: false,
							event_count: 25,
							last_event_at: '2026-01-18T12:00:00Z'
						},
						{
							id: 'repo-2',
							full_name: 'testorg/repo2',
							description: 'Second repository',
							private: true,
							event_count: 10,
							last_event_at: '2026-01-17T08:00:00Z'
						}
					],
					total: 2,
					page: 1,
					per_page: 10
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
		await page.route('/api/repositories*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'repo-1',
							full_name: 'testorg/private-repo',
							description: 'Private repository',
							private: true,
							event_count: 5
						}
					],
					total: 1,
					page: 1,
					per_page: 10
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
	 *     Then the URL should update with the search parameter
	 */
	test('should update URL when searching', async ({ page }) => {
		await page.route('/api/repositories*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 10 })
			});
		});

		await page.goto('/repositories');

		// Act - Type in search box
		const searchInput = page.getByPlaceholder(/search/i);
		await searchInput.fill('my-repo');
		await searchInput.press('Enter');

		// Assert - URL contains search parameter
		await expect(page).toHaveURL(/search=my-repo/);
	});

	/**
	 * AC: Given a user with no connected repositories
	 *     When they visit the repositories page
	 *     Then they should see an empty state
	 */
	test('should display empty state when no repositories', async ({ page }) => {
		await page.route('/api/repositories*', async (route) => {
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
					full_name: 'testorg/my-repo',
					description: 'A great repository for testing',
					private: false,
					event_count: 42,
					last_event_at: '2026-01-18T14:30:00Z',
					html_url: 'https://github.com/testorg/my-repo'
				})
			});
		});

		// Mock events for this repository
		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'event-1',
							event_type: 'push',
							action: null,
							status: 'processed',
							sender_login: 'developer'
						}
					],
					total: 1,
					page: 1,
					per_page: 10
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
					full_name: 'testorg/my-repo',
					event_count: 2
				})
			});
		});

		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'event-1',
							event_type: 'pull_request',
							action: 'opened',
							status: 'processed',
							sender_login: 'user1'
						},
						{
							id: 'event-2',
							event_type: 'push',
							action: null,
							status: 'processed',
							sender_login: 'user2'
						}
					],
					total: 2,
					page: 1,
					per_page: 10
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
					full_name: 'testorg/my-repo',
					html_url: 'https://github.com/testorg/my-repo'
				})
			});
		});

		await page.route('/api/events*', async (route) => {
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
				body: JSON.stringify({ id: 'repo-1', full_name: 'test/repo' })
			});
		});

		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0 })
			});
		});

		await page.route('/api/repositories*', async (route) => {
			if (!route.request().url().includes('/repo-1')) {
				await route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify({ items: [], total: 0 })
				});
			}
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
