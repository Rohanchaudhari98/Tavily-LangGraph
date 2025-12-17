import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getQuery } from '../services/api';
import ResultsDisplay from '../components/ResultsDisplay';
import LoadingSpinner from '../components/LoadingSpinner';

export default function ResultsPage() {
  const { queryId } = useParams();
  const navigate = useNavigate();
  const [queryData, setQueryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchQueryData();
    
    // Poll for updates if processing
    const interval = setInterval(() => {
      if (queryData?.status === 'processing') {
        fetchQueryData();
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [queryId, queryData?.status]);

  const fetchQueryData = async () => {
    try {
      const data = await getQuery(queryId);
      setQueryData(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch query:', err);
      setError('Failed to load query results');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <LoadingSpinner message="Loading query results..." />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="card p-12 text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-red-100 to-rose-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">⚠️</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Error Loading Results</h2>
            <p className="text-gray-600 mb-8 text-lg">{error}</p>
            <button onClick={() => navigate('/')} className="btn-primary">
              Back to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-12">
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Modern Navigation */}
        <div className="mb-8 flex gap-3">
          <button
            onClick={() => navigate('/')}
            className="bg-white hover:bg-gray-50 text-gray-700 font-medium py-2.5 px-5
                       rounded-xl border-2 border-gray-200 hover:border-gray-300
                       shadow-sm hover:shadow-md transition-all duration-200
                       flex items-center gap-2"
          >
            <span>←</span>
            New Analysis
          </button>
          <button
            onClick={() => navigate('/history')}
            className="bg-white hover:bg-gray-50 text-gray-700 font-medium py-2.5 px-5
                       rounded-xl border-2 border-gray-200 hover:border-gray-300
                       shadow-sm hover:shadow-md transition-all duration-200
                       flex items-center gap-2"
          >
            <span>📋</span>
            History
          </button>
          <button
            onClick={fetchQueryData}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700
                       text-white font-medium py-2.5 px-5 rounded-xl
                       shadow-md hover:shadow-lg transition-all duration-200
                       disabled:opacity-50 disabled:cursor-not-allowed
                       flex items-center gap-2"
            disabled={queryData?.status !== 'processing'}
          >
            <span className={queryData?.status === 'processing' ? 'animate-spin' : ''}>🔄</span>
            Refresh
          </button>
        </div>

        {/* Results Display */}
        <ResultsDisplay queryData={queryData} />
      </div>
    </div>
  );
}