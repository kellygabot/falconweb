'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface UserResponse {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  roles: string[];
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Check if already logged in
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      router.push('/admin');
    }
  }, [router]);

  const getDashboardPath = (roles: string[]): string => {
    if (roles.includes('super_admin') || roles.includes('school_admin')) {
      return '/admin';
    }
    if (roles.includes('instructor') || roles.includes('advisor')) {
      return '/faculty';
    }
    if (roles.includes('student')) {
      return '/student';
    }
    return '/admin';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Login
      const loginRes = await api.post<LoginResponse>('/auth/login', {
        email,
        password,
        remember_me: rememberMe,
      });

      if (loginRes.status !== 200 || !loginRes.data) {
        setError(loginRes.error || 'Login failed');
        setLoading(false);
        return;
      }

      // Store tokens
      api.setAccessToken(loginRes.data.access_token);
      api.setRefreshToken(loginRes.data.refresh_token);

      // Get user info to determine dashboard
      const userRes = await api.get<UserResponse>('/auth/me');

      if (userRes.status === 200 && userRes.data) {
        const dashPath = getDashboardPath(userRes.data.roles);
        router.push(dashPath);
      } else {
        setError('Could not fetch user profile');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="w-full max-w-md bg-white rounded-lg shadow p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Falcon School</h1>
          <p className="text-gray-600 mt-2">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div className="flex items-center">
            <input
              id="remember"
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="h-4 w-4 text-indigo-600 rounded border-gray-300"
            />
            <label htmlFor="remember" className="ml-2 text-sm text-gray-700">
              Remember me (30 days)
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          Need help?{' '}
          <Link href="/" className="text-indigo-600 hover:underline">
            Back to home
          </Link>
        </div>
      </div>
    </main>
  );
}
