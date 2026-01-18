<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';

	let isMenuOpen = $state(false);

	function handleLogout() {
		// Redirect to logout endpoint which will clear cookie and redirect back
		window.location.href = '/api/auth/logout';
	}

	function toggleMenu() {
		isMenuOpen = !isMenuOpen;
	}
</script>

<header
	class="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
>
	<div class="container mx-auto flex h-16 items-center justify-between px-4">
		<!-- Logo -->
		<a href="/" class="flex items-center gap-2">
			<span class="text-xl font-bold">🔄 Orchestrator</span>
		</a>

		<!-- Navigation -->
		<nav class="hidden items-center gap-6 md:flex">
			<a
				href="/"
				class="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
			>
				Dashboard
			</a>
			<a
				href="/repositories"
				class="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
			>
				Repositories
			</a>
			<a
				href="/events"
				class="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
			>
				Events
			</a>
		</nav>

		<!-- User Menu -->
		{#if authStore.user}
			<div class="relative">
				<button
					onclick={toggleMenu}
					class="flex items-center gap-2 rounded-full p-1 hover:bg-accent"
					data-testid="user-menu-button"
				>
					{#if authStore.user.github_avatar_url}
						<img
							src={authStore.user.github_avatar_url}
							alt={authStore.user.github_login}
							class="h-8 w-8 rounded-full"
						/>
					{:else}
						<div
							class="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground"
						>
							{authStore.user.github_login[0].toUpperCase()}
						</div>
					{/if}
					<span class="hidden text-sm font-medium md:inline"
						>{authStore.user.github_login}</span
					>
				</button>

				{#if isMenuOpen}
					<div
						class="absolute right-0 mt-2 w-48 rounded-md border bg-popover shadow-lg"
						data-testid="user-menu-dropdown"
					>
						<div class="p-2">
							<div class="px-2 py-1.5 text-sm font-medium">
								{authStore.user.github_name || authStore.user.github_login}
							</div>
							<div class="px-2 py-1.5 text-xs text-muted-foreground">
								@{authStore.user.github_login}
							</div>
						</div>
						<div class="border-t">
							<a
								href="/settings"
								class="block px-4 py-2 text-sm hover:bg-accent"
								onclick={() => (isMenuOpen = false)}
							>
								Settings
							</a>
							<button
								onclick={handleLogout}
								class="w-full px-4 py-2 text-left text-sm hover:bg-accent"
								data-testid="logout-button"
							>
								Logout
							</button>
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</header>
