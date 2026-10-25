import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://abundance-zone-platform.onrender.com';

/**
 * Axios client instance configured for AZYMP backend
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor to add auth token
 */
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage (will be managed by Zustand)
    if (typeof window !== 'undefined') {
      const authStore = localStorage.getItem('auth-storage');
      console.log('🔍 [API Client] Checking auth-storage:', !!authStore);
      
      if (authStore) {
        try {
          const { state } = JSON.parse(authStore);
          const token = state?.accessToken;
          
          console.log('🔑 [API Client] Token found:', !!token);
          if (token) {
            console.log('📝 [API Client] Token preview:', token.substring(0, 30) + '...');
          }
          
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log('✅ [API Client] Authorization header set');
          } else {
            console.warn('⚠️ [API Client] No accessToken in state');
          }
        } catch (error) {
          console.error('❌ [API Client] Error parsing auth store:', error);
        }
      } else {
        console.warn('⚠️ [API Client] No auth-storage in localStorage');
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response interceptor for:
 * 1. Unwrapping ApiResponse envelope
 * 2. Error handling
 * 3. Token refresh
 */
apiClient.interceptors.response.use(
  (response) => {
    // Unwrap ApiResponse envelope if present
    if (response.data && typeof response.data === 'object' && 'success' in response.data && 'data' in response.data) {
      console.log('📦 [API Client] Unwrapping ApiResponse envelope');
      response.data = response.data.data;
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    // Handle 401 - Unauthorized (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt token refresh
        const authStore = localStorage.getItem('auth-storage');
        if (authStore) {
          const { state } = JSON.parse(authStore);
          const refreshToken = state?.refreshToken;

          if (refreshToken) {
            const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
              refreshToken,
            });

            const { accessToken } = response.data;

            // Update stored token
            const newState = { ...state, accessToken };
            localStorage.setItem('auth-storage', JSON.stringify({ state: newState }));

            // Retry original request with new token
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${accessToken}`;
            }
            return apiClient(originalRequest);
          }
        }
      } catch (refreshError) {
        // Refresh failed - redirect to login
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth-storage');
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
