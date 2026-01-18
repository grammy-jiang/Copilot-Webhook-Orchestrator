import { test, expect } from '@playwright/test';

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
		await expect(page.getByRole('heading', { name: /login/i })).toBeVisible();
		await expect(page.getByRole('link', { name: /login with github/i })).toBeVisible();
	});

	/**
	 * AC: Given a user clicks "Login with GitHub"
	 *     When the OAuth flow begins
	 *     Then they should be redirected to the OAuth endpoint
	 */
	test('should redirect to OAuth endpoint when clicking login button', async ({ page }) => {
		// Arrange
		const loginButton = page.getByRole('link', { name: /login with github/i });

		// Assert - Button has correct href
		await expect(loginButton).toHaveAttribute('href', '/api/auth/login');
	});

	/**
	 * AC: Given a user was logged out
	 *     When they visit the login page with logout=true
	 *     Then they should see a logout success message
	 */
	test('should display logout success message when logout=true', async ({ page }) => {
		// Arrange - Visit login with logout parameter
		await page.goto('/login?logout=true');

		// Assert - Success message is visible
		await expect(page.getByText(/logged out successfully/i)).toBeVisible();
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
		await expect(page.getByText(/failed|error|denied/i)).toBeVisible();
	});

	/**
	 * AC: Given the session has expired
	 *     When user visits login page with expired=true
	 *     Then they should see a session expired message
	 */
	test('should display session expired message when expired=true', async ({ page }) => {
		// Arrange - Visit login with expired parameter
		await page.goto('/login?expired=true');

		// Assert - Expired message is visible
		await expect(page.getByText(/session.*expired/i)).toBeVisible();
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
		// Note: This depends on backend auth middleware behavior
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
		// Tab to the login button
		await page.keyboard.press('Tab');

		// Assert - Login button is focused
		const loginButton = page.getByRole('link', { name: /login with github/i });
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
