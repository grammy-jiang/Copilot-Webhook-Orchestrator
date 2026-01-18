<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import ChevronsUpDownIcon from '@lucide/svelte/icons/chevrons-up-down';
	import BadgeCheckIcon from '@lucide/svelte/icons/badge-check';
	import BellIcon from '@lucide/svelte/icons/bell';
	import CreditCardIcon from '@lucide/svelte/icons/credit-card';
	import LogOutIcon from '@lucide/svelte/icons/log-out';
	import SparklesIcon from '@lucide/svelte/icons/sparkles';

	function handleLogout() {
		window.location.href = '/api/auth/logout';
	}

	function navigateToAccount() {
		goto('/account');
	}

	function navigateToBilling() {
		goto('/billing');
	}

	function navigateToNotifications() {
		goto('/notifications');
	}

	const navItems = [
		{
			href: '/',
			label: 'Dashboard',
			icon: 'home'
		},
		{
			href: '/repositories',
			label: 'Repositories',
			icon: 'repo'
		},
		{
			href: '/events',
			label: 'Events',
			icon: 'activity'
		}
	];

	function isActive(href: string): boolean {
		if (href === '/') {
			return page.url.pathname === '/';
		}
		return page.url.pathname.startsWith(href);
	}
</script>

<aside class="flex h-screen w-64 flex-col border-r bg-sidebar text-sidebar-foreground">
	<!-- Logo Header -->
	<div class="flex h-16 items-center gap-2 border-b px-6">
		<div
			class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="h-5 w-5"
			>
				<path d="M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3" />
			</svg>
		</div>
		<span class="font-semibold">Orchestrator</span>
	</div>

	<!-- Navigation -->
	<nav class="flex-1 space-y-1 p-4">
		{#each navItems as item (item.href)}
			<a
				href={item.href}
				class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors {isActive(
					item.href
				)
					? 'bg-sidebar-accent text-sidebar-accent-foreground'
					: 'text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'}"
			>
				{#if item.icon === 'home'}
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="h-4 w-4"
					>
						<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
						<polyline points="9 22 9 12 15 12 15 22" />
					</svg>
				{:else if item.icon === 'repo'}
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="h-4 w-4"
					>
						<path
							d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.28 1.15-.28 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"
						/>
						<path d="M9 18c-4.51 2-5-2-7-2" />
					</svg>
				{:else if item.icon === 'activity'}
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						class="h-4 w-4"
					>
						<polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
					</svg>
				{/if}
				{item.label}
			</a>
		{/each}
	</nav>

	<!-- User Menu Footer -->
	{#if authStore.user}
		{@const user = authStore.user}
		<div class="border-t p-2">
			<DropdownMenu.Root>
				<DropdownMenu.Trigger class="w-full" data-testid="user-menu-button">
					{#snippet child({ props })}
						<button
							{...props}
							class="flex w-full items-center gap-2 rounded-lg p-2 text-left hover:bg-sidebar-accent data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
						>
							{#if user.github_avatar_url}
								<img
									src={user.github_avatar_url}
									alt={user.github_login}
									class="size-8 rounded-lg"
								/>
							{:else}
								<div
									class="flex size-8 items-center justify-center rounded-lg bg-primary text-sm font-medium text-primary-foreground"
								>
									{user.github_login[0].toUpperCase()}
								</div>
							{/if}
							<div class="grid flex-1 text-left text-sm leading-tight">
								<span class="truncate font-medium">
									{user.github_name || user.github_login}
								</span>
								<span class="truncate text-xs text-sidebar-foreground/70">
									@{user.github_login}
								</span>
							</div>
							<ChevronsUpDownIcon class="ml-auto size-4" />
						</button>
					{/snippet}
				</DropdownMenu.Trigger>
				<DropdownMenu.Content
					class="w-[--bits-dropdown-menu-anchor-width] min-w-56 rounded-lg"
					align="end"
					side="top"
					sideOffset={4}
				>
					<DropdownMenu.Label class="p-0 font-normal">
						<div class="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
							{#if user.github_avatar_url}
								<img
									src={user.github_avatar_url}
									alt={user.github_login}
									class="size-8 rounded-lg"
								/>
							{:else}
								<div
									class="flex size-8 items-center justify-center rounded-lg bg-primary text-sm font-medium text-primary-foreground"
								>
									{user.github_login[0].toUpperCase()}
								</div>
							{/if}
							<div class="grid flex-1 text-left text-sm leading-tight">
								<span class="truncate font-medium">
									{user.github_name || user.github_login}
								</span>
								<span class="truncate text-xs text-muted-foreground">
									@{user.github_login}
								</span>
							</div>
						</div>
					</DropdownMenu.Label>
					<DropdownMenu.Separator />
					<DropdownMenu.Group>
						<DropdownMenu.Item>
							<SparklesIcon class="mr-2 size-4" />
							Upgrade to Pro
						</DropdownMenu.Item>
					</DropdownMenu.Group>
					<DropdownMenu.Separator />
					<DropdownMenu.Group>
						<DropdownMenu.Item onSelect={navigateToAccount}>
							<BadgeCheckIcon class="mr-2 size-4" />
							Account
						</DropdownMenu.Item>
						<DropdownMenu.Item onSelect={navigateToBilling}>
							<CreditCardIcon class="mr-2 size-4" />
							Billing
						</DropdownMenu.Item>
						<DropdownMenu.Item onSelect={navigateToNotifications}>
							<BellIcon class="mr-2 size-4" />
							Notifications
						</DropdownMenu.Item>
					</DropdownMenu.Group>
					<DropdownMenu.Separator />
					<DropdownMenu.Item onSelect={handleLogout} data-testid="logout-button">
						<LogOutIcon class="mr-2 size-4" />
						Log out
					</DropdownMenu.Item>
				</DropdownMenu.Content>
			</DropdownMenu.Root>
		</div>
	{/if}
</aside>
