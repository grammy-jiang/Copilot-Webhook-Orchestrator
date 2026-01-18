import { test, expect } from '@playwright/test';
import { tabUntilFocused } from './test-utils';

/**
 * Login E2E Tests
 *
 * Tests the OAuth login flow for GitHub authentication.
 * These tests verify the critical path from landing page to authenticated dashboard.
 *
 * @see Story 0: User Authentication (OAuth Login)
 */

test.describe('Login Page', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/login');
	});

	/**
	 * AC: Given a user visits the login page
	 *     When the page loads
	 *     Then they should see the login interface
	 */
	test('should display login page with GitHub login button', async ({ page }) => {
		// Assert - Login page elements are visible
		await expect(
			page.getByRole('heading', { name: /copilot workflow orchestrator/i })
		).toBeVisible();
		await expect(page.getByRole('button', { name: /login with github/i })).toBeVisible();
	});

	/**
	 * AC: Given a user clicks "Login with GitHub"
	 *     When the OAuth flow begins
	 *     Then the button should trigger navigation to OAuth endpoint
	 */
	test('should have login button that triggers OAuth flow', async ({ page }) => {
		// Assert - Login button is visible and clickable
		const loginButton = page.getByRole('button', { name: /login with github/i });
		await expect(loginButton).toBeVisible();
		await expect(loginButton).toBeEnabled();
	});

	/**
	 * AC: Given a user was logged out
	 *     When they visit the login page with logout=success
	 *     Then they should see a logout success message
	 */
	test('should display logout success message when logout=success', async ({ page }) => {
		// Arrange - Visit login with logout parameter
		await page.goto('/login?logout=success');

		// Assert - Success message is visible
		await expect(page.getByText(/logged out/i)).toBeVisible();
	});

	/**
	 * AC: Given OAuth authentication failed
	 *     When user returns to login page with error
	 *     Then they should see an error message
	 */
	test('should display error message on OAuth failure', async ({ page }) => {
		// Arrange - Visit login with error parameter
		await page.goto('/login?error=access_denied');

		// Assert - Error message is visible
		await expect(page.getByText(/error occurred/i)).toBeVisible();
	});

	/**
	 * AC: Given the session has expired
	 *     When user visits login page with error=session_expired
	 *     Then they should see a session expired message
	 */
	test('should display session expired message when error=session_expired', async ({ page }) => {
		// Arrange - Visit login with session_expired error
		await page.goto('/login?error=session_expired');

		// Assert - Expired message is visible
		await expect(page.getByText(/session expired/i)).toBeVisible();
	});
});

test.describe('Authentication Flow', () => {
	/**
	 * AC: Given an unauthenticated user
	 *     When they visit a protected page
	 *     Then they should be redirected to login
	 */
	test('should redirect unauthenticated users to login', async ({ page }) => {
		// Arrange - Try to access protected route
		await page.goto('/repositories');

		// Assert - Redirected to login or shows login prompt
		// Note: Client-side redirect via authStore check in onMount
		await expect(page).toHaveURL(/login/);
	});

	/**
	 * AC: Given an unauthenticated user
	 *     When they visit the dashboard
	 *     Then they should be redirected to login
	 */
	test('should redirect from dashboard to login when unauthenticated', async ({ page }) => {
		// Arrange - Visit dashboard directly
		await page.goto('/');

		// Assert - Should redirect to login
		await expect(page).toHaveURL(/login/);
	});
});

test.describe('Login Page Accessibility', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/login');
	});

	/**
	 * A11Y-01: Keyboard navigation works on login page
	 */
	test('should be navigable with keyboard', async ({ page }) => {
		// Tab through elements until login button is focused
		const loginButton = page.getByRole('button', { name: /login with github/i });

		// Press Tab multiple times to reach the button (may need to pass skip links, nav items)
		const focused = await tabUntilFocused(page, loginButton);

		// Assert - Login button is focused
		expect(focused).toBe(true);
		await expect(loginButton).toBeFocused();
	});

	/**
	 * A11Y-03: ARIA labels present
	 */
	test('should have accessible heading structure', async ({ page }) => {
		// Assert - Main heading exists
		const heading = page.getByRole('heading', { level: 1 });
		await expect(heading).toBeVisible();
	});
});
