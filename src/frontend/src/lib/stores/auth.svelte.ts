import type { User, Installation } from '$lib/types';

class AuthStore {
	user = $state<User | null>(null);
	installation = $state<Installation | null>(null);
	isLoading = $state(true);
	error = $state<string | null>(null);

	get isAuthenticated(): boolean {
		return this.user !== null;
	}

	get hasInstallation(): boolean {
		return this.installation !== null && this.installation.status === 'active';
	}

	async fetchUser(): Promise<void> {
		this.isLoading = true;
		this.error = null;

		try {
			const response = await fetch('/api/auth/me');
			if (response.ok) {
				const data = await response.json();
				// Backend returns UserResponse directly, not wrapped in { user, installation }
				this.user = data;
				// Fetch installation data
				await this.fetchInstallation();
			} else if (response.status === 401) {
				this.user = null;
				this.installation = null;
			} else {
				throw new Error('Failed to fetch user');
			}
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Unknown error';
			this.user = null;
			this.installation = null;
		} finally {
			this.isLoading = false;
		}
	}

	async fetchInstallation(): Promise<void> {
		try {
			const response = await fetch('/api/installations');
			if (response.ok) {
				const data = await response.json();
				// Get the first active installation
				if (data.installations && data.installations.length > 0) {
					this.installation = data.installations[0];
				} else {
					this.installation = null;
				}
			} else {
				this.installation = null;
			}
		} catch {
			this.installation = null;
		}
	}

	async logout(): Promise<void> {
		try {
			// Use GET request to match the backend logout endpoint
			await fetch('/api/auth/logout', { method: 'GET' });
		} finally {
			this.user = null;
			this.installation = null;
		}
	}

	reset(): void {
		this.user = null;
		this.installation = null;
		this.isLoading = false;
		this.error = null;
	}
}

export const authStore = new AuthStore();
