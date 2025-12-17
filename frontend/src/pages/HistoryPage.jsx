import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { listQueries, deleteQuery } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

export default function HistoryPage() {
  const navigate = useNavigate();
  const [queries, setQueries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchQueries();
  }, []);

  const fetchQueries = async () => {
    try {
      const data = await listQueries(0, 50);
      setQueries(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch queries:', err);
      setError('Failed to load query history');
      setLoading(false);
    }
  };

  const handleDelete = async (queryId) => {
    if (!confirm('Are you sure you want to delete this query?')) {
      return;
    }

    try {
      await deleteQuery(queryId);
      setQueries(queries.filter(q => q.query_id !== queryId));
    } catch (err) {
      console.error('Failed to delete query:', err);
      alert('Failed to delete query');
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      processing: (
        <span className="status-badge-processing">
          <span className="animate-pulse mr-1.5">⏳</span>
          Processing
        </span>
      ),
      completed: (
        <span className="status-badge-completed">
          <span className="mr-1.5">✓</span>
          Completed
        </span>
      ),
      failed: (
        <span className="status-badge-failed">
          <span className="mr-1.5">✗</span>
          Failed
        </span>
      ),
    };

    return badges[status] || badges.completed;
  };

  if (loading) {
    return (
      <div className="min-h-screen py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <LoadingSpinner message="Loading your analyses..." />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-12">
      {/* Modern Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="max-w-6xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-extrabold mb-2">Query History</h1>
              <p className="text-blue-100 text-lg">View and manage your analyses</p>
            </div>
            <button
              onClick={() => navigate('/')}
              className="bg-white text-blue-600 font-semibold py-3 px-6 rounded-xl
                         shadow-lg hover:shadow-xl transform hover:-translate-y-0.5
                         transition-all duration-200 flex items-center gap-2"
            >
              <span className="text-xl">+</span>
              New Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 -mt-8 sm:px-6 lg:px-8">
        {error && (
          <div className="bg-gradient-to-r from-red-50 to-rose-50 border-2 border-red-200 rounded-2xl p-6 mb-8 shadow-lg">
            <div className="flex items-center gap-3">
              <span className="text-3xl">⚠️</span>
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          </div>
        )}

        {queries.length === 0 ? (
          <div className="card p-16 text-center">
            <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-5xl">📊</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">No analyses yet</h3>
            <p className="text-gray-600 mb-8 text-lg">Start by creating your first competitive intelligence analysis</p>
            <button onClick={() => navigate('/')} className="btn-primary text-lg">
              Create First Analysis
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {queries.map((query) => (
              <div key={query.query_id} className="card p-6 hover:shadow-2xl transition-all duration-300">
                <div className="flex items-start justify-between gap-6">
                  <div className="flex-1 min-w-0">
                    {/* Header */}
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-xl font-bold text-gray-900 truncate">
                        {query.company_name}
                      </h3>
                      {getStatusBadge(query.status)}
                    </div>
                    
                    {/* Query text */}
                    <p className="text-gray-700 mb-4 leading-relaxed line-clamp-2">
                      {query.query}
                    </p>
                    
                    {/* Stats */}
                    <div className="flex items-center gap-6 text-sm">
                      <div className="flex items-center gap-2 text-gray-600">
                        <span className="text-blue-600">👥</span>
                        <span className="font-medium">{query.competitor_count}</span>
                        <span>competitors</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <span className="text-green-600">📅</span>
                        <span>{new Date(query.created_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}</span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col gap-2 flex-shrink-0">
                    <button
                      onClick={() => navigate(`/results/${query.query_id}`)}
                      className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700
                                 text-white font-semibold py-2.5 px-6 rounded-xl
                                 shadow-md hover:shadow-lg transition-all duration-200"
                    >
                      View Results
                    </button>
                    <button
                      onClick={() => handleDelete(query.query_id)}
                      className="bg-white hover:bg-red-50 text-red-600 font-medium py-2.5 px-6 
                                 rounded-xl border-2 border-red-200 hover:border-red-300
                                 transition-all duration-200"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}