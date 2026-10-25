/**
 * API Response Types
 * Based on backend FastAPI response structure
 */

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

export type ApiResult<T> = ApiResponse<T> | ApiError;

/**
 * Common Query Parameters
 */
export interface PaginationParams {
  page?: number;
  pageSize?: number;
}

export interface SearchParams {
  search?: string;
}

export interface FilterParams {
  [key: string]: string | number | boolean | undefined;
}

export type QueryParams = PaginationParams & SearchParams & FilterParams;
