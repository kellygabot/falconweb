export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Falcon School</h1>
          <p className="text-gray-600 mt-1">Grading & School Management System</p>
        </div>
      </header>

      <section className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold mb-6">Welcome</h2>

          {/* Facebook Feed Section */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold mb-4">Latest Posts</h3>
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <p className="text-gray-600">
                Loading latest posts from Falcon School Facebook pages...
              </p>
            </div>
          </div>

          {/* Auth Links */}
          <div className="flex gap-4">
            <a
              href="/login"
              className="inline-block bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
            >
              Login
            </a>
            <a
              href="#"
              className="inline-block bg-gray-200 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-300"
            >
              Learn More
            </a>
          </div>
        </div>
      </section>
    </main>
  );
}
