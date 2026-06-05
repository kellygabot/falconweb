'use client';

export default function StudentPortal() {
  return (
    <main className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">My Grades</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Current Subjects
              </h3>
              <div className="space-y-3">
                <div className="border-l-4 border-indigo-500 pl-4 py-2">
                  <p className="font-medium text-gray-900">Mathematics</p>
                  <p className="text-sm text-gray-600">Quiz 1: 78/100</p>
                </div>
                <div className="border-l-4 border-indigo-500 pl-4 py-2">
                  <p className="font-medium text-gray-900">English</p>
                  <p className="text-sm text-gray-600">Essay: 85/100</p>
                </div>
              </div>
            </div>
          </div>

          <div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Course Materials
              </h3>
              <p className="text-sm text-gray-600">
                Download PPT and PDF files from your instructors
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
