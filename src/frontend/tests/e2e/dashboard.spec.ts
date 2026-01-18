import { test, expect } from '@playwright/test';

/**
 * Dashboard E2E Tests
 *
 * Tests the main dashboard page that shows repositories and recent events.
 * These are critical path tests for the authenticated user experience.
 *
 * @see Story 5: Minimal Dashboard
 */

// Helper to mock authenticated state matching authStore expectations
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
					avatar_url: 'https://github.com/testuser.png',
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

test.describe('Dashboard', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthenticatedState(page);
		await page.goto('/');
	});

	/**
	 * AC: Given an authenticated user with installations
	 *     When they visit the dashboard
	 *     Then they should see the dashboard interface
	 */
	test('should display dashboard with header', async ({ page }) => {
		// Assert - Dashboard elements are visible
		await expect(page.getByRole('banner')).toBeVisible();
		await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
	});

	/**
	 * AC: Given a user with connected repositories
	 *     When they view the dashboard
	 *     Then they should see their repositories
	 */
	test('should display repositories section', async ({ page }) => {
		// Mock repositories API (Dashboard uses /api/installations/repositories)
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
							description: 'Test repository 1',
							is_private: false,
							default_branch: 'main',
							event_count: 10,
							last_event_at: '2026-01-18T12:00:00Z'
						}
					],
					total: 1,
					page: 1,
					per_page: 10,
					pages: 1
				})
			});
		});

		await page.reload();

		// Assert - Repository is visible
		await expect(page.getByText('testorg/repo1')).toBeVisible();
	});

	/**
	 * AC: Given a user with recent events
	 *     When they view the dashboard
	 *     Then they should see recent events
	 */
	test('should display recent events section', async ({ page }) => {
		// Mock events API
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
							actor: 'developer',
							processing_status: 'processed',
							created_at: '2026-01-18T14:00:00Z',
							github_timestamp: '2026-01-18T14:00:00Z'
						}
					],
					total: 1,
					page: 1,
					per_page: 5,
					pages: 1
				})
			});
		});

		await page.reload();

		// Assert - Event is visible
		await expect(page.getByText(/pull_request/i)).toBeVisible();
	});

	/**
	 * AC: Given a user clicks on a repository
	 *     When the click completes
	 *     Then they should navigate to repository detail
	 */
	test('should navigate to repository detail on click', async ({ page }) => {
		// Mock repositories API
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
							description: 'Test repository',
							is_private: false,
							default_branch: 'main',
							event_count: 10,
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

		await page.reload();

		// Act - Click on repository card
		await page.getByTestId('repository-card').first().click();

		// Assert - Navigated to repository detail
		await expect(page).toHaveURL(/\/repositories\/repo-1/);
	});
});

test.describe('Dashboard - Empty State', () => {
	test.beforeEach(async ({ page }) => {
		// Mock auth as authenticated but with no installation
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
					installation: null
				})
			});
		});

		await page.goto('/');
	});

	/**
	 * AC: Given a user with no connected repositories
	 *     When they view the dashboard
	 *     Then they should see an empty state with CTA
	 */
	test('should display empty state when no installations', async ({ page }) => {
		// Assert - Empty state is visible
		await expect(page.getByTestId('empty-state')).toBeVisible();
		await expect(page.getByRole('link', { name: /connect repositories/i })).toBeVisible();
	});
});

test.describe('Dashboard - User Menu', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthenticatedState(page);
		await page.goto('/');
	});

	/**
	 * AC: Given an authenticated user
	 *     When they view the header
	 *     Then they should see their user menu
	 */
	test('should display user profile in header', async ({ page }) => {
		// Assert - User menu button is visible (testid is reliable across viewports)
		await expect(page.getByTestId('user-menu-button')).toBeVisible();
	});

	/**
	 * AC: Given a user clicks the logout button
	 *     When the action completes
	 *     Then they should be logged out and redirected
	 */
	test('should logout when clicking logout button', async ({ page }) => {
		// Mock logout API
		await page.route('/api/auth/logout', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ success: true })
			});
		});

		// Act - Open user menu and click logout
		await page.getByTestId('user-menu-button').click();
		await page.getByTestId('logout-button').click();

		// Assert - Redirected to login
		await expect(page).toHaveURL(/\/login/);
	});
});

test.describe('Dashboard Accessibility', () => {
	test.beforeEach(async ({ page }) => {
		await mockAuthenticatedState(page);
		await page.goto('/');
	});

	/**
	 * A11Y-01: Keyboard navigation on dashboard
	 */
	test('should be navigable with keyboard', async ({ page }) => {
		// Tab through interactive elements until something is focused
		for (let i = 0; i < 5; i++) {
			await page.keyboard.press('Tab');
			await page.waitForTimeout(50);
			const count = await page.locator(':focus').count();
			if (count > 0) break;
		}

		// Assert - At least one interactive element can receive focus
		await expect(page.locator(':focus')).not.toHaveCount(0);
	});

	/**
	 * A11Y-03: Main landmark exists
	 */
	test('should have main content landmark', async ({ page }) => {
		// Assert - Main element exists
		await expect(page.getByRole('main')).toBeVisible();
	});
});
