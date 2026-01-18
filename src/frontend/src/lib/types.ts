// User type matching backend schema
export interface User {
	id: string;
	github_id: number;
	username: string;
	email: string | null;
	avatar_url: string | null;
	created_at: string;
}

// Installation type
export interface Installation {
	id: string;
	installation_id: number;
	account_login: string;
	account_type: 'User' | 'Organization';
	is_suspended: boolean;
	created_at: string;
}

// Repository type
export interface Repository {
	id: string;
	github_id: number;
	owner: string;
	name: string;
	full_name: string;
	description: string | null;
	is_private: boolean;
	default_branch: string;
	last_event_at: string | null;
	event_count: number;
}

// Event type
export interface Event {
	id: string;
	delivery_id: string;
	event_type: string;
	event_action: string | null;
	repository_id: string;
	repository_name: string;
	actor: string | null;
	processing_status: 'received' | 'processing' | 'processed' | 'failed';
	created_at: string;
	github_timestamp: string | null;
}

// Pagination
export interface PaginatedResponse<T> {
	items: T[];
	total: number;
	page: number;
	per_page: number;
	pages: number;
}

// Health status
export type HealthStatus = 'healthy' | 'warning' | 'error';
