'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

interface SchoolYear {
  id: string;
  year: number;
  is_current: boolean;
}

interface GradingPeriod {
  id: string;
  name: string;
  type: string;
  order: number;
  is_locked: boolean;
  start_date: string;
  end_date: string;
}

interface Section {
  id: string;
  name: string;
  grade_level: number;
  advisor_id: string;
}

interface Subject {
  id: string;
  name: string;
  code: string;
  instructor_id: string;
}

export default function AdminDashboard() {
  const router = useRouter();
  const [schoolYears, setSchoolYears] = useState<SchoolYear[]>([]);
  const [gradingPeriods, setGradingPeriods] = useState<GradingPeriod[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [currentSchoolYear, setCurrentSchoolYear] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form states
  const [activeTab, setActiveTab] = useState<'overview' | 'years' | 'periods' | 'sections' | 'subjects' | 'users'>('overview');
  const [yearForm, setYearForm] = useState({ year: new Date().getFullYear() });
  const [periodForm, setPeriodForm] = useState({
    name: '',
    type: 'quarter',
    order: 1,
    start_date: '',
    end_date: '',
  });
  const [sectionForm, setSectionForm] = useState({
    name: '',
    grade_level: 9,
    advisor_id: '',
  });
  const [subjectForm, setSubjectForm] = useState({
    section_id: '',
    name: '',
    code: '',
    instructor_id: '',
  });
  const [userForm, setUserForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    roles: ['student'],
  });

  useEffect(() => {
    loadData();
  }, [router]);

  useEffect(() => {
    setError('');
    setSuccess('');
  }, [activeTab]);

  const loadData = async () => {
    try {
      const authRes = await api.get('/auth/me');
      if (authRes.status !== 200) {
        router.push('/login');
        return;
      }

      const yearsRes = await api.get<SchoolYear[]>('/school/school-years');
      if (yearsRes.data) {
        setSchoolYears(yearsRes.data);
        const current = yearsRes.data.find(y => y.is_current);
        if (current) {
          setCurrentSchoolYear(current.id);
          await Promise.all([
            loadGradingPeriods(current.id),
            loadSections(current.id),
          ]);
        }
      }
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadGradingPeriods = async (yearId: string) => {
    const res = await api.get<GradingPeriod[]>(`/school/grading-periods/${yearId}`);
    if (res.data) setGradingPeriods(res.data);
  };

  const loadSections = async (yearId: string) => {
    const res = await api.get<Section[]>(`/school/sections/${yearId}`);
    if (res.data) setSections(res.data);
  };

  const handleCreateYear = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await api.post('/school/school-years', yearForm);
    if (res.status === 200) {
      setSuccess('School year created!');
      setYearForm({ year: new Date().getFullYear() + 1 });
      await loadData();
    } else {
      setError(res.error || 'Failed to create school year');
    }
  };

  const handleCreatePeriod = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentSchoolYear) {
      setError('Select a school year first');
      return;
    }
    const res = await api.post('/school/grading-periods', {
      school_year_id: currentSchoolYear,
      ...periodForm,
    });
    if (res.status === 200) {
      setSuccess('Grading period created!');
      setPeriodForm({ name: '', type: 'quarter', order: 1, start_date: '', end_date: '' });
      await loadGradingPeriods(currentSchoolYear);
    } else {
      setError(res.error || 'Failed to create period');
    }
  };

  const handleCreateSection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentSchoolYear) {
      setError('Select a school year first');
      return;
    }
    const res = await api.post('/school/sections', {
      school_year_id: currentSchoolYear,
      ...sectionForm,
    });
    if (res.status === 200) {
      setSuccess('Section created!');
      setSectionForm({ name: '', grade_level: 9, advisor_id: '' });
      await loadSections(currentSchoolYear);
    } else {
      setError(res.error || 'Failed to create section');
    }
  };

  const handleCreateSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentSchoolYear) {
      setError('Select a school year first');
      return;
    }
    const res = await api.post('/school/subjects', {
      school_year_id: currentSchoolYear,
      ...subjectForm,
    });
    if (res.status === 200) {
      setSuccess('Subject created!');
      setSubjectForm({ section_id: '', name: '', code: '', instructor_id: '' });
    } else {
      setError(res.error || 'Failed to create subject');
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await api.post('/users/', userForm);
    if (res.status === 200) {
      setSuccess('User created!');
      setUserForm({ email: '', first_name: '', last_name: '', password: '', roles: ['student'] });
    } else {
      setError(res.error || 'Failed to create user');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/login');
  };

  if (loading) return <div className="p-8 text-center">Loading...</div>;

  return (
    <main className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          <button
            onClick={handleLogout}
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded mb-6">{error}</div>
        )}
        {success && (
          <div className="bg-green-50 text-green-700 p-4 rounded mb-6">{success}</div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b flex-wrap">
          {(['overview', 'years', 'periods', 'sections', 'subjects', 'users'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium border-b-2 capitalize ${
                activeTab === tab
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-2">School Years</h3>
              <p className="text-3xl font-bold text-indigo-600">{schoolYears.length}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-2">Grading Periods</h3>
              <p className="text-3xl font-bold text-blue-600">{gradingPeriods.length}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-2">Sections</h3>
              <p className="text-3xl font-bold text-green-600">{sections.length}</p>
            </div>
          </div>
        )}

        {/* School Years Tab */}
        {activeTab === 'years' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Create School Year</h2>
              <form onSubmit={handleCreateYear} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Year</label>
                  <input
                    type="number"
                    value={yearForm.year}
                    onChange={e => setYearForm({ year: parseInt(e.target.value) })}
                    className="mt-1 w-full border rounded px-3 py-2"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
                >
                  Create School Year
                </button>
              </form>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">School Years</h2>
              <div className="space-y-2">
                {schoolYears.map(year => (
                  <div
                    key={year.id}
                    onClick={() => {
                      setCurrentSchoolYear(year.id);
                      loadGradingPeriods(year.id);
                      loadSections(year.id);
                    }}
                    className={`p-3 rounded cursor-pointer ${
                      currentSchoolYear === year.id
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 hover:bg-gray-200'
                    }`}
                  >
                    SY {year.year}-{year.year + 1} {year.is_current && '(Current)'}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Grading Periods Tab */}
        {activeTab === 'periods' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Create Grading Period</h2>
              <form onSubmit={handleCreatePeriod} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium">Name (e.g., Q1, Q2)</label>
                  <input
                    value={periodForm.name}
                    onChange={e => setPeriodForm({ ...periodForm, name: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Type</label>
                  <select
                    value={periodForm.type}
                    onChange={e => setPeriodForm({ ...periodForm, type: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                  >
                    <option>quarter</option>
                    <option>semester</option>
                    <option>midterm</option>
                    <option>finals</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium">Order</label>
                  <input
                    type="number"
                    value={periodForm.order}
                    onChange={e => setPeriodForm({ ...periodForm, order: parseInt(e.target.value) })}
                    className="mt-1 w-full border rounded px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Start Date</label>
                  <input
                    type="date"
                    value={periodForm.start_date}
                    onChange={e => setPeriodForm({ ...periodForm, start_date: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">End Date</label>
                  <input
                    type="date"
                    value={periodForm.end_date}
                    onChange={e => setPeriodForm({ ...periodForm, end_date: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
                >
                  Create Period
                </button>
              </form>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Periods</h2>
              <div className="space-y-2">
                {gradingPeriods.map(period => (
                  <div key={period.id} className="p-3 bg-gray-50 rounded">
                    <p className="font-medium">{period.name}</p>
                    <p className="text-xs text-gray-600">
                      {period.start_date} to {period.end_date}
                    </p>
                    <p className="text-xs text-gray-600">
                      {period.is_locked ? '🔒 Locked' : 'Open'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Sections Tab */}
        {activeTab === 'sections' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Create Section</h2>
              <form onSubmit={handleCreateSection} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium">Section Name (e.g., 3-A)</label>
                  <input
                    value={sectionForm.name}
                    onChange={e => setSectionForm({ ...sectionForm, name: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Grade Level (7-12)</label>
                  <input
                    type="number"
                    min="7"
                    max="12"
                    value={sectionForm.grade_level}
                    onChange={e => setSectionForm({ ...sectionForm, grade_level: parseInt(e.target.value) })}
                    className="mt-1 w-full border rounded px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Advisor ID</label>
                  <input
                    value={sectionForm.advisor_id}
                    onChange={e => setSectionForm({ ...sectionForm, advisor_id: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    placeholder="Paste user ID here"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
                >
                  Create Section
                </button>
              </form>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Sections</h2>
              <div className="space-y-2">
                {sections.map(section => (
                  <div key={section.id} className="p-3 bg-gray-50 rounded">
                    <p className="font-medium">{section.name}</p>
                    <p className="text-xs text-gray-600">Grade {section.grade_level}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Subjects Tab */}
        {activeTab === 'subjects' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Create Subject</h2>
            <form onSubmit={handleCreateSubject} className="space-y-4 max-w-2xl">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">Section ID</label>
                  <input
                    value={subjectForm.section_id}
                    onChange={e => setSubjectForm({ ...subjectForm, section_id: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    placeholder="Paste section ID"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Subject Name</label>
                  <input
                    value={subjectForm.name}
                    onChange={e => setSubjectForm({ ...subjectForm, name: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    placeholder="e.g., Mathematics"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">Subject Code</label>
                  <input
                    value={subjectForm.code}
                    onChange={e => setSubjectForm({ ...subjectForm, code: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    placeholder="e.g., MATH-3"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Instructor ID</label>
                  <input
                    value={subjectForm.instructor_id}
                    onChange={e => setSubjectForm({ ...subjectForm, instructor_id: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    placeholder="Paste user ID"
                    required
                  />
                </div>
              </div>
              <button
                type="submit"
                className="w-full bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
              >
                Create Subject
              </button>
            </form>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Create User</h2>
            <form onSubmit={handleCreateUser} className="space-y-4 max-w-2xl">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium">First Name</label>
                  <input
                    value={userForm.first_name}
                    onChange={e => setUserForm({ ...userForm, first_name: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium">Last Name</label>
                  <input
                    value={userForm.last_name}
                    onChange={e => setUserForm({ ...userForm, last_name: e.target.value })}
                    className="mt-1 w-full border rounded px-3 py-2"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium">Email</label>
                <input
                  type="email"
                  value={userForm.email}
                  onChange={e => setUserForm({ ...userForm, email: e.target.value })}
                  className="mt-1 w-full border rounded px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium">Password</label>
                <input
                  type="password"
                  value={userForm.password}
                  onChange={e => setUserForm({ ...userForm, password: e.target.value })}
                  className="mt-1 w-full border rounded px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium">Role</label>
                <select
                  value={userForm.roles[0]}
                  onChange={e => setUserForm({ ...userForm, roles: [e.target.value] })}
                  className="mt-1 w-full border rounded px-3 py-2"
                >
                  <option value="student">Student</option>
                  <option value="instructor">Instructor</option>
                  <option value="advisor">Advisor</option>
                  <option value="school_admin">School Admin</option>
                </select>
              </div>
              <button
                type="submit"
                className="w-full bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
              >
                Create User
              </button>
            </form>
          </div>
        )}
      </div>
    </main>
  );
}
