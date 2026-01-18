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
							delivery_id: 'delivery-1',
							event_type: 'pull_request',
							event_action: 'opened',
							repository_id: 'repo-1',
							repository_name: 'testorg/repo1',
							actor: 'developer1',
							processing_status: 'processed',
							created_at: '2026-01-18T14:00:00Z',
							github_timestamp: '2026-01-18T14:00:00Z'
						},
						{
							id: 'event-2',
							delivery_id: 'delivery-2',
							event_type: 'push',
							event_action: null,
							repository_id: 'repo-1',
							repository_name: 'testorg/repo1',
							actor: 'developer2',
							processing_status: 'processed',
							created_at: '2026-01-18T13:00:00Z',
							github_timestamp: '2026-01-18T13:00:00Z'
						},
						{
							id: 'event-3',
							delivery_id: 'delivery-3',
							event_type: 'issues',
							event_action: 'closed',
							repository_id: 'repo-2',
							repository_name: 'testorg/repo2',
							actor: 'maintainer',
							processing_status: 'failed',
							created_at: '2026-01-18T12:00:00Z',
							github_timestamp: '2026-01-18T12:00:00Z'
						}
					],
					total: 3,
					page: 1,
					per_page: 10,
					pages: 1
				})
			});
		});

		await page.goto('/events');

		// Assert - All events visible
		await expect(page.getByText(/pull_request/i)).toBeVisible();
		await expect(page.getByText(/push/i)).toBeVisible();
		await expect(page.getByText(/issues/i)).toBeVisible();
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
							delivery_id: 'delivery-1',
							event_type: 'push',
							event_action: null,
							repository_id: 'repo-1',
							repository_name: 'test/repo',
							actor: null,
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
							repository_name: 'test/repo',
							actor: null,
							processing_status: 'failed',
							created_at: '2026-01-18T13:00:00Z',
							github_timestamp: null
						},
						{
							id: 'event-3',
							delivery_id: 'delivery-3',
							event_type: 'push',
							event_action: null,
							repository_id: 'repo-1',
							repository_name: 'test/repo',
							actor: null,
							processing_status: 'received',
							created_at: '2026-01-18T12:00:00Z',
							github_timestamp: null
						}
					],
					total: 3,
					page: 1,
					per_page: 10,
					pages: 1
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
	 *     Then the event list should be filtered
	 */
	test('should filter events by status', async ({ page }) => {
		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 10, pages: 0 })
			});
		});

		await page.goto('/events');

		// Act - Select status filter (implementation uses select elements)
		const statusFilter = page.locator('select').nth(1);
		await statusFilter.selectOption('failed');

		// Assert - Filter was applied (select has value)
		await expect(statusFilter).toHaveValue('failed');
	});

	/**
	 * AC: Given a user selects an event type filter
	 *     When the filter is applied
	 *     Then the event list should be filtered
	 */
	test('should filter events by type', async ({ page }) => {
		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 10, pages: 0 })
			});
		});

		await page.goto('/events');

		// Act - Select type filter (first select is for type)
		const typeFilter = page.locator('select').first();
		await typeFilter.selectOption('pull_request');

		// Assert - Filter was applied (select has value)
		await expect(typeFilter).toHaveValue('pull_request');
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
				body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 10, pages: 0 })
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
						delivery_id: `delivery-${i}`,
						event_type: 'push',
						event_action: null,
						repository_id: 'repo-1',
						repository_name: 'test/repo',
						actor: null,
						processing_status: 'processed',
						created_at: '2026-01-18T14:00:00Z',
						github_timestamp: null
					})),
					total: 50,
					page: 1,
					per_page: 10,
					pages: 5
				})
			});
		});

		await page.goto('/events');

		// Assert - Pagination visible
		await expect(page.getByRole('button', { name: /next/i })).toBeVisible();
	});

	/**
	 * AC: Given a user clicks next page
	 *     When pagination changes
	 *     Then the page number should update
	 */
	test('should navigate to next page', async ({ page }) => {
		await page.route('/api/events*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: Array.from({ length: 10 }, (_, i) => ({
						id: `event-${i}`,
						delivery_id: `delivery-${i}`,
						event_type: 'push',
						event_action: null,
						repository_id: 'repo-1',
						repository_name: 'test/repo',
						actor: null,
						processing_status: 'processed',
						created_at: '2026-01-18T14:00:00Z',
						github_timestamp: null
					})),
					total: 50,
					page: 1,
					per_page: 10,
					pages: 5
				})
			});
		});

		await page.goto('/events');

		// Act - Click next page
		await page.getByRole('button', { name: /next/i }).click();

		// Assert - Page 2 indicator visible
		await expect(page.getByText(/page 2/i)).toBeVisible();
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
					event: {
						id: 'event-1',
						delivery_id: 'abc123',
						event_type: 'pull_request',
						event_action: 'opened',
						repository_id: 'repo-1',
						repository_name: 'testorg/repo1',
						actor: 'developer',
						processing_status: 'processed',
						created_at: '2026-01-18T14:30:00Z',
						github_timestamp: '2026-01-18T14:30:00Z'
					},
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
					event: {
						id: 'event-1',
						delivery_id: 'delivery-1',
						event_type: 'push',
						event_action: null,
						repository_id: 'repo-1',
						repository_name: 'test/repo',
						actor: null,
						processing_status: 'processed',
						created_at: '2026-01-18T14:30:00Z',
						github_timestamp: null
					},
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
					event: {
						id: 'event-1',
						delivery_id: 'delivery-1',
						event_type: 'push',
						event_action: null,
						repository_id: 'repo-1',
						repository_name: 'test/repo',
						actor: null,
						processing_status: 'processed',
						created_at: '2026-01-18T14:30:00Z',
						github_timestamp: '2026-01-18T14:30:00Z'
					},
					payload: null
				})
			});
		});

		await page.goto('/events/event-1');

		// Assert - Time info visible (format may vary)
		await expect(page.getByText(/received/i)).toBeVisible();
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
					event: {
						id: 'event-1',
						delivery_id: 'delivery-1',
						event_type: 'push',
						event_action: null,
						repository_id: 'repo-1',
						repository_name: 'test/repo',
						actor: null,
						processing_status: 'processed',
						created_at: '2026-01-18T14:30:00Z',
						github_timestamp: null
					},
					payload: null
				})
			});
		});

		await page.route('/api/events', async (route) => {
			if (!route.request().url().includes('/event-1')) {
				await route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify({ items: [], total: 0, page: 1, per_page: 20, pages: 0 })
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
					event: {
						id: 'event-1',
						delivery_id: 'delivery-1',
						event_type: 'push',
						event_action: null,
						repository_id: 'repo-1',
						repository_name: 'testorg/repo1',
						actor: null,
						processing_status: 'processed',
						created_at: '2026-01-18T14:30:00Z',
						github_timestamp: null
					},
					payload: null
				})
			});
		});

		await page.route('/api/repositories/repo-1', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'repo-1',
					github_id: 111,
					owner: 'testorg',
					name: 'repo1',
					full_name: 'testorg/repo1',
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
							delivery_id: 'delivery-1',
							event_type: 'push',
							event_action: null,
							repository_id: 'repo-1',
							repository_name: 'test/repo',
							actor: null,
							processing_status: 'processed',
							created_at: '2026-01-18T14:00:00Z',
							github_timestamp: null
						}
					],
					total: 1,
					page: 1,
					per_page: 10,
					pages: 1
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
