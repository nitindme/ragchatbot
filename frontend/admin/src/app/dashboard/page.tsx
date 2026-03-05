'use client';

import { useState, useEffect } from 'react';
import { 
  listDocuments, 
  uploadDocument, 
  deleteDocument,
  listSessions,
  getAllFeedback,
  getFeedbackStats,
  markFeedbackReviewed
} from '@/lib/api';

interface Document {
  id: string;
  filename: string;
  created_at: string;
}

interface ChatSession {
  session_id: string;
  created_at: string;
  message_count: number;
}

interface Feedback {
  id: number;
  session_id: string;
  message: string;
  feedback_type: string;
  is_helpful: boolean;
  comment?: string;
  created_at: string;
  reviewed: boolean;
}

interface FeedbackStats {
  total: number;
  helpful: number;
  not_helpful: number;
  with_comments: number;
  pending_review: number;
}

type TabType = 'documents' | 'sessions' | 'feedback';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabType>('documents');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [token, setToken] = useState('');

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      window.location.href = '/';
      return;
    }
    setToken(storedToken);
    loadDocuments(storedToken);
    loadSessions();
    loadFeedback();
  }, []);

  const loadDocuments = async (authToken: string) => {
    try {
      const docs = await listDocuments(authToken);
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSessions = async () => {
    try {
      const data = await listSessions();
      setSessions(data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const loadFeedback = async () => {
    try {
      const [feedbackData, stats] = await Promise.all([
        getAllFeedback(),
        getFeedbackStats()
      ]);
      setFeedback(feedbackData);
      setFeedbackStats(stats);
    } catch (error) {
      console.error('Failed to load feedback:', error);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !token) return;

    setUploading(true);
    try {
      await uploadDocument(file, token);
      await loadDocuments(token);
      alert('Document uploaded successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await deleteDocument(id, token);
      await loadDocuments(token);
      alert('Document deleted successfully!');
    } catch (error) {
      alert('Failed to delete document');
    }
  };

  const handleMarkReviewed = async (feedbackId: number) => {
    try {
      await markFeedbackReviewed(feedbackId, token);
      await loadFeedback();
    } catch (error) {
      console.error('Failed to mark as reviewed:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="bg-white shadow">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Admin Dashboard</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4">
          <div className="flex gap-8">
            <button
              onClick={() => setActiveTab('documents')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'documents'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Documents ({documents.length})
            </button>
            <button
              onClick={() => setActiveTab('sessions')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'sessions'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Chat Sessions ({sessions.length})
            </button>
            <button
              onClick={() => setActiveTab('feedback')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'feedback'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Feedback ({feedback.length})
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Documents Tab */}
        {activeTab === 'documents' && (
          <>
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4">Upload Document</h2>
              <div className="flex items-center gap-4">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  accept=".pdf,.txt,.docx"
                  disabled={uploading}
                  className="flex-1"
                />
                {uploading && <span className="text-gray-600">Uploading...</span>}
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Supported formats: PDF, TXT, DOCX (Max 10MB)
              </p>
            </div>

            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 border-b">
                <h2 className="text-xl font-semibold">Documents ({documents.length})</h2>
              </div>

              {documents.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  No documents uploaded yet
                </div>
              ) : (
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Filename
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Uploaded
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {documents.map((doc) => (
                      <tr key={doc.id}>
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{doc.filename}</div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {new Date(doc.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={() => handleDelete(doc.id)}
                            className="text-red-600 hover:text-red-900 text-sm font-medium"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}

        {/* Sessions Tab */}
        {activeTab === 'sessions' && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b">
              <h2 className="text-xl font-semibold">Chat Sessions ({sessions.length})</h2>
            </div>

            {sessions.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                No chat sessions yet
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Session ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Messages
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {sessions.map((session) => (
                    <tr key={session.session_id}>
                      <td className="px-6 py-4">
                        <div className="text-sm font-mono text-gray-900">
                          {session.session_id.substring(0, 8)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(session.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {session.message_count}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Feedback Tab */}
        {activeTab === 'feedback' && (
          <>
            {/* Stats Cards */}
            {feedbackStats && (
              <div className="grid grid-cols-5 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-500">Total</div>
                  <div className="text-2xl font-bold">{feedbackStats.total}</div>
                </div>
                <div className="bg-green-50 rounded-lg shadow p-4">
                  <div className="text-sm text-green-600">Helpful</div>
                  <div className="text-2xl font-bold text-green-600">{feedbackStats.helpful}</div>
                </div>
                <div className="bg-red-50 rounded-lg shadow p-4">
                  <div className="text-sm text-red-600">Not Helpful</div>
                  <div className="text-2xl font-bold text-red-600">{feedbackStats.not_helpful}</div>
                </div>
                <div className="bg-blue-50 rounded-lg shadow p-4">
                  <div className="text-sm text-blue-600">With Comments</div>
                  <div className="text-2xl font-bold text-blue-600">{feedbackStats.with_comments}</div>
                </div>
                <div className="bg-yellow-50 rounded-lg shadow p-4">
                  <div className="text-sm text-yellow-600">Pending Review</div>
                  <div className="text-2xl font-bold text-yellow-600">{feedbackStats.pending_review}</div>
                </div>
              </div>
            )}

            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 border-b">
                <h2 className="text-xl font-semibold">User Feedback ({feedback.length})</h2>
              </div>

              {feedback.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  No feedback yet
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {feedback.map((fb) => (
                    <div key={fb.id} className="px-6 py-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              fb.is_helpful 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {fb.is_helpful ? '👍 Helpful' : '👎 Not Helpful'}
                            </span>
                            <span className="text-xs text-gray-500">
                              {new Date(fb.created_at).toLocaleString()}
                            </span>
                            {fb.reviewed && (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                ✓ Reviewed
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-700 mb-1">
                            <span className="font-medium">Message:</span> {fb.message}
                          </div>
                          {fb.comment && (
                            <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded mt-2">
                              <span className="font-medium">Comment:</span> {fb.comment}
                            </div>
                          )}
                          <div className="text-xs text-gray-400 mt-1">
                            Session: {fb.session_id.substring(0, 8)}...
                          </div>
                        </div>
                        {!fb.reviewed && (
                          <button
                            onClick={() => handleMarkReviewed(fb.id)}
                            className="ml-4 px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                          >
                            Mark Reviewed
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
