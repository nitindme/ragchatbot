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
  status?: string;
  file_size?: number;
  total_chunks?: number;
  page_count?: number;
  processing_error?: string;
  updated_at?: string;
}

interface ChatSession {
  id: string;
  created_at: string;
  message_count: number;
  user_messages: number;
  assistant_messages: number;
  first_message?: string;
  last_message?: string;
  last_activity: string;
}

interface Feedback {
  id: number;
  session_id: string;
  message_id: string;
  question: string;
  response: string;
  rating: number;
  rating_text: string;
  comment?: string;
  is_reviewed: boolean;
  created_at: string;
  reviewed_at?: string;
  sources?: string[];
  has_comment: boolean;
  time_ago: string;
}

interface FeedbackStats {
  total_feedback: number;
  positive: number;
  negative: number;
  unreviewed: number;
  with_comments: number;
  recent_7_days: number;
  average_rating: number;
  satisfaction_rate: number;
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

  const loadDocuments = async (authToken: string) => {
    console.log('🔄 loadDocuments called, token:', authToken?.substring(0, 20) + '...');
    try {
      console.log('📡 Calling listDocuments API...');
      const docs = await listDocuments(authToken);
      console.log('✅ Documents loaded:', docs.length, 'documents');
      setDocuments(docs);
    } catch (error) {
      console.error('❌ Failed to load documents:', error);
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

  useEffect(() => {
    console.log('🚀 Initial useEffect running...');
    const storedToken = localStorage.getItem('token');
    console.log('🔑 Token from localStorage:', storedToken ? 'Found (' + storedToken.substring(0, 20) + '...)' : 'NOT FOUND');
    
    if (!storedToken) {
      console.log('❌ No token, redirecting to login...');
      window.location.href = '/';
      return;
    }
    
    setToken(storedToken);
    console.log('📥 Loading initial data...');
    
    // Load all data in parallel and set loading to false when done
    Promise.all([
      loadDocuments(storedToken),
      loadSessions(),
      loadFeedback()
    ]).finally(() => {
      console.log('🏁 All initial data loaded, setting loading to false');
      setLoading(false);
    });
  }, []);
  
  // Separate effect for polling - only polls when there are pending/processing docs
  useEffect(() => {
    console.log('🔍 Polling useEffect triggered. Token:', !!token, 'Docs:', documents.length);
    
    if (!token || documents.length === 0) {
      console.log('⏸️ Skipping polling - no token or no documents yet');
      return;
    }
    
    const hasPendingDocs = documents.some(doc => 
      doc.status === 'pending' || doc.status === 'processing'
    );
    
    console.log('📊 Documents status check:', {
      total: documents.length,
      pending: documents.filter(d => d.status === 'pending').length,
      processing: documents.filter(d => d.status === 'processing').length,
      hasPendingDocs
    });
    
    if (!hasPendingDocs) {
      console.log('✋ No pending docs, skipping polling');
      return;
    }
    
    console.log('⏰ Starting polling interval (5s)...');
    const pollInterval = setInterval(() => {
      console.log('🔄 Polling tick...');
      loadDocuments(token);
    }, 5000);
    
    return () => {
      console.log('🛑 Clearing polling interval');
      clearInterval(pollInterval);
    };
  }, [documents, token]);

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
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Details
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
                      <tr key={doc.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{doc.filename}</div>
                          {doc.file_size && (
                            <div className="text-xs text-gray-500">
                              {(doc.file_size / 1024 / 1024).toFixed(2)} MB
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {doc.status === 'completed' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              ✓ Completed
                            </span>
                          )}
                          {doc.status === 'processing' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              ⏳ Processing...
                            </span>
                          )}
                          {doc.status === 'pending' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              ⏳ Pending
                            </span>
                          )}
                          {doc.status === 'failed' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              ✗ Failed
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {doc.status === 'completed' && (
                            <div className="text-sm text-gray-600">
                              <div>{doc.page_count} pages</div>
                              <div>{doc.total_chunks} chunks</div>
                            </div>
                          )}
                          {doc.status === 'failed' && doc.processing_error && (
                            <div className="text-xs text-red-600" title={doc.processing_error}>
                              {doc.processing_error.substring(0, 50)}...
                            </div>
                          )}
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
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Session ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        First Message
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Last Message
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Messages
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Created
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Last Activity
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {sessions.map((session) => (
                      <tr key={session.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="text-xs font-mono text-gray-900">
                            {session.id.substring(0, 12)}...
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-700 max-w-xs truncate">
                            {session.first_message || 'N/A'}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-700 max-w-xs truncate">
                            {session.last_message || 'N/A'}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-col gap-1">
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-100 text-blue-800">
                              Total: {session.message_count}
                            </span>
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-green-100 text-green-800">
                              User: {session.user_messages}
                            </span>
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-purple-100 text-purple-800">
                              Bot: {session.assistant_messages}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-xs text-gray-500">
                          {new Date(session.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-xs text-gray-500">
                          {new Date(session.last_activity).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Feedback Tab */}
        {activeTab === 'feedback' && (
          <>
            {/* Stats Cards */}
            {feedbackStats && (
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
                <div className="bg-white rounded-lg shadow p-4">
                  <div className="text-sm text-gray-500">Total Feedback</div>
                  <div className="text-2xl font-bold">{feedbackStats.total_feedback}</div>
                </div>
                <div className="bg-green-50 rounded-lg shadow p-4">
                  <div className="text-sm text-green-600">👍 Helpful</div>
                  <div className="text-2xl font-bold text-green-600">{feedbackStats.positive}</div>
                </div>
                <div className="bg-red-50 rounded-lg shadow p-4">
                  <div className="text-sm text-red-600">👎 Not Helpful</div>
                  <div className="text-2xl font-bold text-red-600">{feedbackStats.negative}</div>
                </div>
                <div className="bg-blue-50 rounded-lg shadow p-4">
                  <div className="text-sm text-blue-600">💬 With Comments</div>
                  <div className="text-2xl font-bold text-blue-600">{feedbackStats.with_comments}</div>
                </div>
                <div className="bg-yellow-50 rounded-lg shadow p-4">
                  <div className="text-sm text-yellow-600">⏳ Pending</div>
                  <div className="text-2xl font-bold text-yellow-600">{feedbackStats.unreviewed}</div>
                </div>
                <div className="bg-purple-50 rounded-lg shadow p-4">
                  <div className="text-sm text-purple-600">📊 Satisfaction</div>
                  <div className="text-2xl font-bold text-purple-600">{feedbackStats.satisfaction_rate}%</div>
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
                    <div key={fb.id} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          {/* Header with rating and time */}
                          <div className="flex items-center gap-2 mb-3">
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                              fb.rating === 1
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {fb.rating_text}
                            </span>
                            <span className="text-sm text-gray-500">
                              {fb.time_ago}
                            </span>
                            {fb.is_reviewed && (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                ✓ Reviewed
                              </span>
                            )}
                            {fb.has_comment && (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                💬 Has Comment
                              </span>
                            )}
                          </div>
                          
                          {/* Question */}
                          <div className="mb-3">
                            <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Question</div>
                            <div className="text-sm text-gray-900 bg-blue-50 p-3 rounded">
                              {fb.question}
                            </div>
                          </div>
                          
                          {/* Response */}
                          <div className="mb-3">
                            <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Bot Response</div>
                            <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                              {fb.response}
                            </div>
                          </div>
                          
                          {/* Sources */}
                          {fb.sources && fb.sources.length > 0 && (
                            <div className="mb-3">
                              <div className="text-xs font-semibold text-gray-500 uppercase mb-1">Sources</div>
                              <div className="flex flex-wrap gap-1">
                                {fb.sources.map((source, idx) => (
                                  <span key={idx} className="inline-flex items-center px-2 py-1 rounded text-xs bg-indigo-100 text-indigo-800">
                                    📄 {source}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* User Comment */}
                          {fb.comment && (
                            <div className="mb-3">
                              <div className="text-xs font-semibold text-gray-500 uppercase mb-1">User Comment</div>
                              <div className="text-sm text-gray-900 bg-yellow-50 p-3 rounded border-l-4 border-yellow-400">
                                {fb.comment}
                              </div>
                            </div>
                          )}
                          
                          {/* Metadata */}
                          <div className="flex items-center gap-4 text-xs text-gray-400 mt-2">
                            <span>Session: {fb.session_id.substring(0, 8)}...</span>
                            <span>Message: {fb.message_id.substring(0, 8)}...</span>
                            <span>Created: {new Date(fb.created_at).toLocaleString()}</span>
                            {fb.reviewed_at && (
                              <span>Reviewed: {new Date(fb.reviewed_at).toLocaleString()}</span>
                            )}
                          </div>
                        </div>
                        
                        {/* Action Button */}
                        {!fb.is_reviewed && (
                          <button
                            onClick={() => handleMarkReviewed(fb.id)}
                            className="ml-4 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            Mark as Reviewed
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
