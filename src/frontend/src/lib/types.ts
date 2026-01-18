// User type matching backend UserResponse schema
export interface User {
	id: number;
	github_id: number;
	github_login: string;
	github_name: string | null;
	github_email: string | null;
	github_avatar_url: string | null;
	last_login_at: string | null;
	created_at: string;
}

// Installation type matching backend InstallationResponse schema
export interface Installation {
	id: number;
	github_installation_id: number;
	account_type: string;
	account_login: string;
	status: string;
	created_at: string;
}

// Installation list response matching backend InstallationListResponse
export interface InstallationListResponse {
	installations: Installation[];
	total: number;
}

// Repository type matching backend Repository model
export interface Repository {
	id: number;
	github_repo_id: number;
	installation_id: number;
	full_name: string;
	owner: string;
	name: string;
	private: boolean;
	default_branch: string;
	created_at: string;
	updated_at: string;
}

// Event type matching backend EventResponse schema
export interface Event {
	id: number;
	delivery_id: string;
	event_type: string;
	action: string | null;
	repository_id: number | null;
	processed: boolean;
	created_at: string;
}

// Event list response matching backend EventListResponse
export interface EventListResponse {
	events: Event[];
	total: number;
	limit: number;
	offset: number;
}

// Event query params matching backend EventQueryParams
export interface EventQueryParams {
	event_type?: string;
	repository_id?: number;
	limit?: number;
	offset?: number;
}

// Health response matching backend HealthResponse
export interface HealthResponse {
	status: string;
	version: string;
	timestamp: string;
}

// Auth error response matching backend AuthErrorResponse
export interface AuthErrorResponse {
	error: string;
	error_description?: string;
}

// Webhook response matching backend WebhookResponse
export interface WebhookResponse {
	status: string;
	delivery_id: string;
	event_type: string;
}

// Generic paginated response for future use
export interface PaginatedResponse<T> {
	items: T[];
	total: number;
	page: number;
	per_page: number;
	pages: number;
}

// Health status type
export type HealthStatus = 'healthy' | 'warning' | 'error';
