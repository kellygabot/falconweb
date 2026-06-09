'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

interface UserInfo {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  roles: string[];
}

interface Subject {
  id: string;
  name: string;
  code: string;
  instructor_id: string;
  section_id: string;
  school_year_id: string;
}

interface GradingPeriod {
  id: string;
  school_year_id: string;
  name: string;
  type: string;
  order: number;
  is_locked: boolean;
  start_date: string;
  end_date: string;
}

interface GradeComponent {
  id: string;
  name: string;
  weight: number;
  order: number;
}

interface GradeSheetStudent {
  student_id: string;
  student_name: string;
  grades: Record<string, number | null>;
}

interface GradeSheet {
  subject_id: string;
  subject_name: string;
  grading_period_id: string;
  is_locked: boolean;
  components: GradeComponent[];
  students: GradeSheetStudent[];
}

export default function FacultyDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [periods, setPeriods] = useState<GradingPeriod[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('');
  const [gradeSheet, setGradeSheet] = useState<GradeSheet | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isMobile, setIsMobile] = useState(false);
  const [savingGrades, setSavingGrades] = useState(false);

  useEffect(() => {
    // Check mobile
    setIsMobile(window.innerWidth < 1024);
    window.addEventListener('resize', () => {
      setIsMobile(window.innerWidth < 1024);
    });

    loadData();
  }, [router]);

  const loadData = async () => {
    try {
      // Get current user
      const authRes = await api.get<UserInfo>('/auth/me');
      if (authRes.status !== 200 || !authRes.data) {
        router.push('/login');
        return;
      }

      setUser(authRes.data);

      // Check if user is instructor or advisor
      const isInstructor = authRes.data.roles.includes('instructor');
      const isAdvisor = authRes.data.roles.includes('advisor');

      if (!isInstructor && !isAdvisor) {
        router.push('/student');
        return;
      }

      // Load subjects for this instructor
      if (isInstructor) {
        const subjectsRes = await api.get<Subject[]>(
          `/school/subjects-by-instructor/${authRes.data.id}`
        );
        if (subjectsRes.data) {
          setSubjects(subjectsRes.data);
        }
      }

      // Load school years to get grading periods
      const yearsRes = await api.get('/school/school-years');
      if (yearsRes.data && Array.isArray(yearsRes.data)) {
        const currentYear = (yearsRes.data as any[]).find(y => y.is_current);
        if (currentYear) {
          // Load periods for this year
          const periodsRes = await api.get<GradingPeriod[]>(
            `/school/grading-periods/${currentYear.id}`
          );
          if (periodsRes.data) {
            setPeriods(periodsRes.data);
          }
        }
      }
    } catch (err) {
      console.error(err);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadGradeSheet = async (subjectId: string, periodId: string) => {
    if (!subjectId || !periodId) {
      setError('Please select both subject and period');
      return;
    }

    setError('');
    const res = await api.get<GradeSheet>(
      `/grades/sheet/${subjectId}?grading_period_id=${periodId}`
    );

    if (res.status === 200 && res.data) {
      setGradeSheet(res.data);
    } else {
      setError(res.error || 'Failed to load grade sheet');
    }
  };

  const handleSaveGrades = async () => {
    if (!gradeSheet || !user) return;

    setSavingGrades(true);
    setError('');
    setSuccess('');

    try {
      const gradeInputs = document.querySelectorAll('input[type="number"]') as NodeListOf<HTMLInputElement>;
      let savedCount = 0;
      let errorCount = 0;

      for (let i = 0; i < gradeInputs.length; i++) {
        const input = gradeInputs[i];
        const value = input.value;

        if (value) {
          const studentId = input.dataset.studentId;
          const componentId = input.dataset.componentId;

          if (!studentId || !componentId) continue;

          const res = await api.post('/grades/update', {
            student_id: studentId,
            subject_id: gradeSheet.subject_id,
            component_id: componentId,
            score: parseFloat(value),
            entered_by: user.id,
          });

          if (res.status === 200) {
            savedCount++;
          } else {
            errorCount++;
          }
        }
      }

      if (savedCount > 0) {
        setSuccess(`Successfully saved ${savedCount} grades${errorCount > 0 ? ` (${errorCount} failed)` : ''}!`);
      } else {
        setError('No grades entered to save');
      }
    } catch (err) {
      setError('Failed to save grades');
      console.error(err);
    } finally {
      setSavingGrades(false);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
        <div className="text-center">Loading...</div>
      </main>
    );
  }

  if (isMobile) {
    return (
      <main className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Faculty Dashboard</h1>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
            <p className="text-yellow-800 font-medium">📱 Grade Sheet Not Available on Mobile</p>
            <p className="text-yellow-700 text-sm mt-2">
              The grade sheet interface is optimized for desktop viewing. Please use a laptop or desktop computer to enter grades.
            </p>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900">Upload Files</h3>
              <p className="text-gray-600 mt-2">Upload course materials (PPT, PDF)</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900">Attendance</h3>
              <p className="text-gray-600 mt-2">Mark student attendance</p>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Grade Sheet</h1>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded mb-6">{error}</div>
        )}

        {/* User Info */}
        {user && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-blue-900">
              Welcome, {user.first_name} {user.last_name}
            </p>
            <p className="text-sm text-blue-700">
              {user.roles.join(', ')}
            </p>
          </div>
        )}

        {success && (
          <div className="bg-green-50 text-green-700 p-4 rounded mb-6">{success}</div>
        )}

        {/* Selection Controls */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Subject</label>
              <select
                value={selectedSubject}
                onChange={e => setSelectedSubject(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              >
                <option value="">
                  {subjects.length === 0 ? 'No subjects assigned' : 'Select a subject...'}
                </option>
                {subjects.map(subject => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name} ({subject.code})
                  </option>
                ))}
              </select>
              {subjects.length === 0 && (
                <p className="text-xs text-gray-500 mt-1">
                  Contact admin to assign you to subjects
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Grading Period</label>
              <select
                value={selectedPeriod}
                onChange={e => setSelectedPeriod(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 border p-2"
              >
                <option value="">
                  {periods.length === 0 ? 'No periods available' : 'Select a period...'}
                </option>
                {periods.map(period => (
                  <option key={period.id} value={period.id}>
                    {period.name} {period.is_locked ? '🔒' : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={() => loadGradeSheet(selectedSubject, selectedPeriod)}
            disabled={!selectedSubject || !selectedPeriod}
            className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Load Grade Sheet
          </button>
        </div>

        {/* Grade Sheet */}
        {gradeSheet && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-xl font-bold">{gradeSheet.subject_name}</h2>
              <p className="text-gray-600">
                {gradeSheet.is_locked ? '🔒 This period is locked' : 'Period is open for editing'}
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-100 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold">Student</th>
                    {gradeSheet.components.map(comp => (
                      <th key={comp.id} className="px-4 py-3 text-center font-semibold">
                        {comp.name}
                        <div className="text-xs text-gray-600">{comp.weight}%</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {gradeSheet.students.map((student, idx) => (
                    <tr key={student.student_id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-4 py-3 font-medium">{student.student_name}</td>
                      {gradeSheet.components.map(comp => (
                        <td key={comp.id} className="px-4 py-3 text-center">
                          <input
                            type="number"
                            min="0"
                            max="100"
                            defaultValue={student.grades[comp.id] ?? ''}
                            disabled={gradeSheet.is_locked}
                            data-student-id={student.student_id}
                            data-component-id={comp.id}
                            className="w-16 text-center border rounded px-2 py-1 disabled:bg-gray-100"
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {!gradeSheet.is_locked && (
              <div className="p-6 border-t">
                <button
                  onClick={handleSaveGrades}
                  disabled={savingGrades}
                  className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {savingGrades ? 'Saving...' : 'Save Grades'}
                </button>
                <p className="text-xs text-gray-500 mt-2">
                  Changes are saved to the database when you click this button
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
