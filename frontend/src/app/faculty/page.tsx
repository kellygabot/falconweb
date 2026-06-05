'use client';

export default function FacultyDashboard() {
  return (
    <main className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Faculty Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900">Grade Sheet</h3>
            <p className="text-gray-600 mt-2">Manage grades for your subjects</p>
            <p className="text-sm text-gray-500 mt-4">📱 Available on desktop only</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900">Attendance</h3>
            <p className="text-gray-600 mt-2">Mark student attendance</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900">Upload Files</h3>
            <p className="text-gray-600 mt-2">Upload course materials (PPT, PDF)</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900">Audit Logs</h3>
            <p className="text-gray-600 mt-2">View history of changes</p>
          </div>
        </div>
      </div>
    </main>
  );
}
