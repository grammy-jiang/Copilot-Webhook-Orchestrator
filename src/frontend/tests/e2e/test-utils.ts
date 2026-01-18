/**
 * E2E Test Utilities and Constants
 *
 * Shared utilities for Playwright E2E tests to ensure consistency
 * and reduce magic numbers across test files.
 */

/**
 * Maximum number of Tab key presses to try when finding focusable elements.
 * This accounts for skip links, navigation items, and other focusable elements
 * that may appear before the target element.
 */
export const MAX_TAB_PRESSES = 10;

/**
 * Number of Tab presses for quick focus checks (dashboard, events list).
 * Used when we just need to verify that something is focusable.
 */
export const QUICK_TAB_PRESSES = 5;

/**
 * Delay in milliseconds between Tab presses to allow focus to settle.
 */
export const TAB_DELAY_MS = 50;

/**
 * Helper function to tab through elements until a target is focused or max attempts reached.
 *
 * @param page - Playwright Page object
 * @param targetLocator - Locator for the element we want to focus
 * @param maxAttempts - Maximum number of Tab presses (default: MAX_TAB_PRESSES)
 * @returns true if target was focused, false otherwise
 */
export async function tabUntilFocused(
	page: import('@playwright/test').Page,
	targetLocator: import('@playwright/test').Locator,
	maxAttempts: number = MAX_TAB_PRESSES
): Promise<boolean> {
	for (let i = 0; i < maxAttempts; i++) {
		await page.keyboard.press('Tab');
		if (await targetLocator.evaluate((el) => document.activeElement === el)) {
			return true;
		}
	}
	return false;
}

/**
 * Helper function to tab through elements until any element is focused.
 *
 * @param page - Playwright Page object
 * @param maxAttempts - Maximum number of Tab presses
 * @returns true if any element (not body) is focused
 */
export async function tabUntilAnyFocused(
	page: import('@playwright/test').Page,
	maxAttempts: number = QUICK_TAB_PRESSES
): Promise<boolean> {
	for (let i = 0; i < maxAttempts; i++) {
		await page.keyboard.press('Tab');
		await page.waitForTimeout(TAB_DELAY_MS);
		const count = await page.locator(':focus').count();
		if (count > 0) return true;
	}
	return false;
}
