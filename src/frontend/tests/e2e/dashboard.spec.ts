import { test, expect } from '@playwright/test';

/**
 * Dashboard E2E Tests
 *
 * Tests the main dashboard page that shows repositories and recent events.
 * These are critical path tests for the authenticated user experience.
 *
 * @see Story 5: Minimal Dashboard
 */

test.describe('Dashboard', () => {
	// Note: These tests assume authenticated state via mock API or test fixtures
	// In a real setup, you would need to mock the auth state

	test.beforeEach(async ({ page }) => {
		// Mock the auth API to return authenticated state
		await page.route('/api/auth/me', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'user-1',
					login: 'testuser',
					name: 'Test User',
					avatar_url: 'https://github.com/testuser.png'
				})
			});
		});

		// Mock installations API
		await page.route('/api/installations', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{
						id: 'install-1',
						account_login: 'testorg',
						account_type: 'Organization',
						installed_at: '2026-01-15T10:00:00Z'
					}
				])
			});
		});

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
		await expect(page.getByText(/dashboard/i)).toBeVisible();
	});

	/**
	 * AC: Given a user with connected repositories
	 *     When they view the dashboard
	 *     Then they should see their repositories
	 */
	test('should display repositories section', async ({ page }) => {
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
							description: 'Test repository 1',
							private: false,
							event_count: 10,
							last_event_at: '2026-01-18T12:00:00Z'
						}
					],
					total: 1,
					page: 1,
					per_page: 10
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
							event_type: 'pull_request',
							action: 'opened',
							status: 'processed',
							repository_full_name: 'testorg/repo1',
							sender_login: 'developer',
							received_at: '2026-01-18T14:00:00Z'
						}
					],
					total: 1,
					page: 1,
					per_page: 5
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
		await page.route('/api/repositories*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					items: [
						{
							id: 'repo-1',
							full_name: 'testorg/repo1',
							description: 'Test repository',
							private: false,
							event_count: 10
						}
					],
					total: 1,
					page: 1,
					per_page: 10
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
		// Mock auth as authenticated
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

		// Mock empty installations
		await page.route('/api/installations', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([])
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
		await expect(page.getByRole('link', { name: /connect|install/i })).toBeVisible();
	});
});

test.describe('Dashboard - User Menu', () => {
	test.beforeEach(async ({ page }) => {
		// Mock auth
		await page.route('/api/auth/me', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 'user-1',
					login: 'testuser',
					name: 'Test User',
					avatar_url: 'https://github.com/testuser.png'
				})
			});
		});

		await page.route('/api/installations', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([{ id: 'install-1' }])
			});
		});

		await page.goto('/');
	});

	/**
	 * AC: Given an authenticated user
	 *     When they view the header
	 *     Then they should see their user menu
	 */
	test('should display user profile in header', async ({ page }) => {
		// Assert - User info is visible
		await expect(page.getByText('testuser')).toBeVisible();
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

		// Act - Click logout
		await page.getByRole('button', { name: /logout/i }).click();

		// Assert - Redirected to login
		await expect(page).toHaveURL(/\/login/);
	});
});

test.describe('Dashboard Accessibility', () => {
	test.beforeEach(async ({ page }) => {
		await page.route('/api/auth/me', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ id: 'user-1', login: 'testuser' })
			});
		});

		await page.route('/api/installations', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([{ id: 'install-1' }])
			});
		});

		await page.goto('/');
	});

	/**
	 * A11Y-01: Keyboard navigation on dashboard
	 */
	test('should be navigable with keyboard', async ({ page }) => {
		// Tab through interactive elements
		await page.keyboard.press('Tab');

		// Assert - Something is focused
		const focusedElement = page.locator(':focus');
		await expect(focusedElement).toBeVisible();
	});

	/**
	 * A11Y-03: Main landmark exists
	 */
	test('should have main content landmark', async ({ page }) => {
		// Assert - Main element exists
		await expect(page.getByRole('main')).toBeVisible();
	});
});
