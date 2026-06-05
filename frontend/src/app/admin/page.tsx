'use client';

export default function AdminDashboard() {
  return (
    <main className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900">Users</h3>
            <p className="text-gray-600 mt-2">Manage accounts and roles</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900">School Settings</h3>
            <p className="text-gray-600 mt-2">Transmutation table, grading periods</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900">Report Card Designer</h3>
            <p className="text-gray-600 mt-2">Design templates for export</p>
          </div>
        </div>
      </div>
    </main>
  );
}
