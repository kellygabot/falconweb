'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

interface Grade {
  subject: string;
  component: string;
  score: number;
}

interface CourseFile {
  id: string;
  filename: string;
  file_size: number;
  created_at: string;
}

interface UserInfo {
  id: string;
  first_name: string;
  last_name: string;
  roles: string[];
}

export default function StudentPortal() {
  const router = useRouter();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'grades' | 'files'>('grades');

  useEffect(() => {
    loadUserData();
  }, [router]);

  const loadUserData = async () => {
    try {
      const res = await api.get<UserInfo>('/auth/me');

      if (res.status !== 200 || !res.data) {
        router.push('/login');
        return;
      }

      // Check if user is a student
      if (!res.data.roles.includes('student')) {
        router.push('/admin');
        return;
      }

      setUser(res.data);
    } catch (err) {
      router.push('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/login');
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
        <div className="text-center">Loading...</div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
        <div className="text-center">Redirecting...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome, {user.first_name}!
            </h1>
            <p className="text-gray-600 mt-1">Student Portal</p>
          </div>
          <button
            onClick={handleLogout}
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b">
          <button
            onClick={() => setActiveTab('grades')}
            className={`px-4 py-2 font-medium border-b-2 ${
              activeTab === 'grades'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            My Grades
          </button>
          <button
            onClick={() => setActiveTab('files')}
            className={`px-4 py-2 font-medium border-b-2 ${
              activeTab === 'files'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Course Materials
          </button>
        </div>

        {/* Grades Tab */}
        {activeTab === 'grades' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">My Grades</h2>

            <div className="space-y-4">
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4 border-l-4 border-blue-500">
                <p className="font-medium text-gray-900">Mathematics - Q1</p>
                <div className="mt-3 grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Quiz 1</p>
                    <p className="text-lg font-bold text-blue-600">78/100</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Quiz 2</p>
                    <p className="text-lg font-bold text-blue-600">82/100</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Midterm</p>
                    <p className="text-lg font-bold text-blue-600">75/100</p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4 border-l-4 border-green-500">
                <p className="font-medium text-gray-900">English - Q1</p>
                <div className="mt-3 grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Essay 1</p>
                    <p className="text-lg font-bold text-green-600">85/100</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Essay 2</p>
                    <p className="text-lg font-bold text-green-600">88/100</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Recitation</p>
                    <p className="text-lg font-bold text-green-600">90/100</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
              <p className="text-sm text-blue-800">
                ℹ️ You see your individual component scores. Final grades are computed by your instructor and are visible after each grading period closes.
              </p>
            </div>
          </div>
        )}

        {/* Files Tab */}
        {activeTab === 'files' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Course Materials</h2>

            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                <div>
                  <p className="font-medium text-gray-900">Math - Chapter 1 Presentation.pptx</p>
                  <p className="text-sm text-gray-600">2.4 MB • Uploaded 3 days ago</p>
                </div>
                <button className="text-indigo-600 hover:text-indigo-700 font-medium">
                  Download
                </button>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                <div>
                  <p className="font-medium text-gray-900">English - Lesson Notes.pdf</p>
                  <p className="text-sm text-gray-600">1.2 MB • Uploaded 1 week ago</p>
                </div>
                <button className="text-indigo-600 hover:text-indigo-700 font-medium">
                  Download
                </button>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                <div>
                  <p className="font-medium text-gray-900">Science - Lab Manual.pdf</p>
                  <p className="text-sm text-gray-600">3.5 MB • Uploaded 2 weeks ago</p>
                </div>
                <button className="text-indigo-600 hover:text-indigo-700 font-medium">
                  Download
                </button>
              </div>
            </div>

            {/* Empty state */}
            <div className="text-center py-8 text-gray-500">
              <p>No files yet for some of your subjects</p>
              <p className="text-sm">Instructors will upload materials as the term progresses</p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
