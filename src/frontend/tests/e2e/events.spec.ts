import { test, expect } from '@playwright/test';

/**
 * Events E2E Tests
 *
 * Tests the event list and detail pages.
 *
 * @see Story 4: Event Stream Viewer
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

test.describe('Event List Page', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthenticatedState(page);
	});

	/**
	 * AC: Given a user with webhook events
	 *     When they visit the events page
	 *     Then they should see their events listed
	 */
	test('should display list of events', async ({ page }) => {
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
							repository_full_name: 'testorg/repo1',
							sender_login: 'developer1',
							received_at: '2026-01-18T14:00:00Z'
						},
						{
							id: 'event-2',
							event_type: 'push',
							action: null,
							status: 'processed',
							repository_full_name: 'testorg/repo1',
							sender_login: 'developer2',
							received_at: '2026-01-18T13:00:00Z'
						},
						{
							id: 'event-3',
							event_type: 'issues',
							action: 'closed',
							status: 'failed',
							repository_full_name: 'testorg/repo2',
							sender_login: 'maintainer',
							received_at: '2026-01-18T12:00:00Z'
						}
					],
					total: 3,
					page: 1,
					per_page: 10
				})
			});
		});

		await page.goto('/events');

		// Assert - All events visible
		await expect(page.getByText(/pull_request.*opened/i)).toBeVisible();
		await expect(page.getByText(/push/i)).toBeVisible();
		await expect(page.getByText(/issues.*closed/i)).toBeVisible();
	});

	/**
	 * AC: Given a user views the event list
	 *     When events have different statuses
	 *     Then they should display appropriate status indicators
	 */
	test('should display event status indicators', async ({ page }) => {
		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'event-1',
							event_type: 'push',
							status: 'processed',
							repository_full_name: 'test/repo'
						},
						{
							id: 'event-2',
							event_type: 'push',
							status: 'failed',
							repository_full_name: 'test/repo'
						},
						{
							id: 'event-3',
							event_type: 'push',
							status: 'received',
							repository_full_name: 'test/repo'
						}
					],
					total: 3,
					page: 1,
					per_page: 10
				})
			});
		});

		await page.goto('/events');

		// Assert - Status texts visible
		await expect(page.getByText('processed')).toBeVisible();
		await expect(page.getByText('failed')).toBeVisible();
		await expect(page.getByText('received')).toBeVisible();
	});

	/**
	 * AC: Given a user selects a status filter
	 *     When the filter is applied
	 *     Then the URL should update
	 */
	test('should update URL when filtering by status', async ({ page }) => {
		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 10 })
			});
		});

		await page.goto('/events');

		// Act - Select status filter
		const statusFilter = page.getByLabel(/status/i);
		await statusFilter.selectOption('failed');

		// Assert - URL contains status parameter
		await expect(page).toHaveURL(/status=failed/);
	});

	/**
	 * AC: Given a user selects an event type filter
	 *     When the filter is applied
	 *     Then the URL should update
	 */
	test('should update URL when filtering by event type', async ({ page }) => {
		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 10 })
			});
		});

		await page.goto('/events');

		// Act - Select type filter
		const typeFilter = page.getByLabel(/type/i);
		await typeFilter.selectOption('pull_request');

		// Assert - URL contains type parameter
		await expect(page).toHaveURL(/type=pull_request/);
	});

	/**
	 * AC: Given a user with no events
	 *     When they visit the events page
	 *     Then they should see an empty state
	 */
	test('should display empty state when no events', async ({ page }) => {
		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 10 })
			});
		});

		await page.goto('/events');

		// Assert - Empty state message
		await expect(page.getByText(/no events|empty/i)).toBeVisible();
	});

	/**
	 * AC: Given there are more events than one page
	 *     When the user is on page 1
	 *     Then they should see pagination controls
	 */
	test('should display pagination when many events', async ({ page }) => {
		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: Array.from({ length: 10 }, (_, i) => ({
						id: `event-${i}`,
						event_type: 'push',
						status: 'processed',
						repository_full_name: 'test/repo'
					})),
					total: 50,
					page: 1,
					per_page: 10
				})
			});
		});

		await page.goto('/events');

		// Assert - Pagination visible
		await expect(page.getByRole('button', { name: /next|page 2|›/i })).toBeVisible();
	});

	/**
	 * AC: Given a user clicks next page
	 *     When pagination changes
	 *     Then the URL should update with page number
	 */
	test('should navigate to next page', async ({ page }) => {
		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: Array.from({ length: 10 }, (_, i) => ({
						id: `event-${i}`,
						event_type: 'push',
						status: 'processed',
						repository_full_name: 'test/repo'
					})),
					total: 50,
					page: 1,
					per_page: 10
				})
			});
		});

		await page.goto('/events');

		// Act - Click next page
		await page.getByRole('button', { name: /next|›/i }).click();

		// Assert - URL has page parameter
		await expect(page).toHaveURL(/page=2/);
	});
});

test.describe('Event Detail Page', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthenticatedState(page);
	});

	/**
	 * AC: Given a user clicks on an event
	 *     When they navigate to the detail page
	 *     Then they should see full event information
	 */
	test('should display event details', async ({ page }) => {
		await page.route('/api/events/event-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'event-1',
					event_type: 'pull_request',
					action: 'opened',
					status: 'processed',
					repository_full_name: 'testorg/repo1',
					sender_login: 'developer',
					received_at: '2026-01-18T14:30:00Z',
					processed_at: '2026-01-18T14:30:01Z',
					delivery_id: 'abc123',
					payload: {
						action: 'opened',
						pull_request: {
							number: 42,
							title: 'Add new feature'
						}
					}
				})
			});
		});

		await page.goto('/events/event-1');

		// Assert - Event info visible
		await expect(page.getByText('pull_request')).toBeVisible();
		await expect(page.getByText('opened')).toBeVisible();
		await expect(page.getByText('testorg/repo1')).toBeVisible();
		await expect(page.getByText('@developer')).toBeVisible();
	});

	/**
	 * AC: Given a user views event detail
	 *     When the event has a payload
	 *     Then they should see the raw JSON payload
	 */
	test('should display raw JSON payload', async ({ page }) => {
		await page.route('/api/events/event-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'event-1',
					event_type: 'push',
					status: 'processed',
					repository_full_name: 'test/repo',
					payload: {
						ref: 'refs/heads/main',
						commits: [{ message: 'Test commit' }]
					}
				})
			});
		});

		await page.goto('/events/event-1');

		// Assert - Payload section visible with JSON content
		await expect(page.getByText(/payload/i)).toBeVisible();
		await expect(page.getByText(/refs\/heads\/main/)).toBeVisible();
	});

	/**
	 * AC: Given a user views event detail
	 *     When timestamps are present
	 *     Then they should be formatted readably
	 */
	test('should display formatted timestamps', async ({ page }) => {
		await page.route('/api/events/event-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'event-1',
					event_type: 'push',
					status: 'processed',
					repository_full_name: 'test/repo',
					received_at: '2026-01-18T14:30:00Z',
					processed_at: '2026-01-18T14:30:05Z'
				})
			});
		});

		await page.goto('/events/event-1');

		// Assert - Time info visible (format may vary)
		await expect(page.getByText(/received|processed/i)).toBeVisible();
	});
});

test.describe('Event Navigation', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthenticatedState(page);
	});

	/**
	 * AC: Given a user is on event detail
	 *     When they click "Back to Events"
	 *     Then they should return to the list
	 */
	test('should navigate back to event list', async ({ page }) => {
		await page.route('/api/events/event-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'event-1',
					event_type: 'push',
					status: 'processed',
					repository_full_name: 'test/repo'
				})
			});
		});

		await page.route('/api/events', async (route) => {
			if (!route.request().url().includes('/event-1')) {
				await route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify({ items: [], total: 0 })
				});
			}
		});

		await page.goto('/events/event-1');

		// Act - Click back link
		await page
			.getByRole('link', { name: /back|events/i })
			.first()
			.click();

		// Assert - On event list
		await expect(page).toHaveURL(/\/events$/);
	});

	/**
	 * AC: Given an event is associated with a repository
	 *     When the user clicks the repository link
	 *     Then they should navigate to that repository
	 */
	test('should navigate to repository from event', async ({ page }) => {
		await page.route('/api/events/event-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'event-1',
					event_type: 'push',
					status: 'processed',
					repository_id: 'repo-1',
					repository_full_name: 'testorg/repo1'
				})
			});
		});

		await page.route('/api/repositories/repo-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ id: 'repo-1', full_name: 'testorg/repo1' })
			});
		});

		await page.route('/api/events*', async (route) => {
			if (route.request().url().includes('repository=')) {
				await route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify({ items: [], total: 0 })
				});
			}
		});

		await page.goto('/events/event-1');

		// Act - Click repository link
		await page.getByRole('link', { name: 'testorg/repo1' }).click();

		// Assert - Navigated to repository
		await expect(page).toHaveURL(/\/repositories\/repo-1/);
	});
});

test.describe('Events Accessibility', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthenticatedState(page);

		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'event-1',
							event_type: 'push',
							status: 'processed',
							repository_full_name: 'test/repo'
						}
					],
					total: 1,
					page: 1,
					per_page: 10
				})
			});
		});
	});

	/**
	 * A11Y-01: Keyboard navigation on events page
	 */
	test('should be navigable with keyboard', async ({ page }) => {
		await page.goto('/events');

		// Tab through interactive elements
		await page.keyboard.press('Tab');

		// Assert - Something is focused
		const focusedElement = page.locator(':focus');
		await expect(focusedElement).toBeVisible();
	});

	/**
	 * A11Y-03: Filter controls are accessible
	 */
	test('should have accessible filter controls', async ({ page }) => {
		await page.goto('/events');

		// Assert - Filter labels exist
		await expect(page.getByLabel(/status|type/i)).toBeVisible();
	});
});
