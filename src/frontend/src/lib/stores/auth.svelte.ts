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
		return this.installation !== null && !this.installation.is_suspended;
	}

	async fetchUser(): Promise<void> {
		this.isLoading = true;
		this.error = null;

		try {
			const response = await fetch('/api/auth/me');
			if (response.ok) {
				const data = await response.json();
				this.user = data.user;
				this.installation = data.installation ?? null;
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

	async logout(): Promise<void> {
		try {
			await fetch('/api/auth/logout', { method: 'POST' });
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
