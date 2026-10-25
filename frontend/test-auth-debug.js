// Quick test to see what's in localStorage after login
const stored = localStorage.getItem('auth-storage');
if (stored) {
  const parsed = JSON.parse(stored);
  console.log('🔍 Auth Storage:', JSON.stringify(parsed, null, 2));
  console.log('✅ Access Token Present?', !!parsed?.state?.accessToken);
  console.log('📝 Token Preview:', parsed?.state?.accessToken?.substring(0, 30) + '...');
} else {
  console.log('❌ No auth-storage found');
}
