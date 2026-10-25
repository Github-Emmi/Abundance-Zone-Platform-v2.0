import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../stores/authStore';
import { authApi, type LoginRequest, type RegisterRequest } from '../api/auth-api';
import { toast } from 'sonner';

/**
 * Hook for login functionality
 */
export const useLogin = () => {
  const { setTokens, setUser } = useAuthStore();

  return useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: async (data) => {
      setTokens({
        accessToken: data.accessToken,
        refreshToken: data.refreshToken,
      });
      setUser(data.user);
      
      // CRITICAL FIX: Wait for Zustand to persist to localStorage
      // before redirecting. This ensures the token is available
      // when the page reloads.
      await new Promise(resolve => setTimeout(resolve, 100));
      
      toast.success('Login successful!');
      // Don't redirect here - let the calling component handle it
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Login failed. Please try again.');
    },
  });
};

/**
 * Hook for registration
 */
export const useRegister = () => {
  const { setTokens, setUser } = useAuthStore();

  return useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: async (data) => {
      setTokens({
        accessToken: data.accessToken,
        refreshToken: data.refreshToken,
      });
      setUser(data.user);
      
      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));
      
      toast.success('Registration successful!');
      // Let calling component handle redirect
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Registration failed. Please try again.');
    },
  });
};

/**
 * Hook for logout
 */
export const useLogout = () => {
  const { logout } = useAuthStore();
  const router = useRouter();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      logout();
      queryClient.clear();
      window.location.href = '/login';
      toast.success('Logged out successfully');
    },
    onError: () => {
      // Logout locally even if API call fails
      logout();
      queryClient.clear();
      window.location.href = '/login';
    },
  });
};

/**
 * Hook to get current user
 */
export const useCurrentUser = () => {
  const { user, isAuthenticated } = useAuthStore();

  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => authApi.me(),
    enabled: isAuthenticated && !user,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  });
};

/**
 * Hook for password reset request
 */
export const useForgotPassword = () => {
  return useMutation({
    mutationFn: (email: string) => authApi.forgotPassword(email),
    onSuccess: () => {
      toast.success('Password reset email sent. Please check your inbox.');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to send reset email.');
    },
  });
};

/**
 * Hook for password reset
 */
export const useResetPassword = () => {
  const router = useRouter();

  return useMutation({
    mutationFn: ({ token, password }: { token: string; password: string }) =>
      authApi.resetPassword(token, password),
    onSuccess: () => {
      toast.success('Password reset successful. Please login with your new password.');
      router.push('/login');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Password reset failed.');
    },
  });
};

/**
 * Hook to check authentication status
 */
export const useIsAuthenticated = () => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated;
};

/**
 * Hook to get user role
 */
export const useUserRole = () => {
  const { user } = useAuthStore();
  return user?.role;
};
