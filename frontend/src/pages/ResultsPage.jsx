// Page to display results of a specific query
// Handles loading, error states, and polling for updates if the query is processing

import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getQuery } from '../services/api';
import ResultsDisplay from '../components/ResultsDisplay';
import LoadingSpinner from '../components/LoadingSpinner';

export default function ResultsPage() {
  const { queryId } = useParams(); // Extract query ID from route
  const navigate = useNavigate();

  const [queryData, setQueryData] = useState(null); // Stores query result
  const [loading, setLoading] = useState(true); // Loading state
  const [error, setError] = useState(null); // Error state
  const statusRef = useRef(null); // Track current status to avoid stale closure

  // Fetch query data on mount and set up polling for processing queries
  useEffect(() => {
    fetchQueryData();

    // Poll every 3 seconds while query is processing
    const interval = setInterval(() => {
      // Check current status from ref (always up-to-date)
      if (!statusRef.current || statusRef.current === 'processing') {
        fetchQueryData();
      }
    }, 3000);

    // Clear interval on unmount
    return () => clearInterval(interval);
  }, [queryId]);

  // Function to fetch query details from API
  const fetchQueryData = async () => {
    try {
      const data = await getQuery(queryId);
      setQueryData(data);
      statusRef.current = data?.status; // Update ref with latest status
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch query:', err);
      setError('Failed to load query results');
      setLoading(false);
    }
  };

  // Show loading spinner while fetching data
  if (loading) {
    return (
      <div className="min-h-screen py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <LoadingSpinner message="Loading query results..." />
        </div>
      </div>
    );
  }

  // Show error message if fetching fails
  if (error) {
    return (
      <div className="min-h-screen py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="card p-12 text-center">
            {/* Error icon */}
            <div className="w-20 h-20 bg-gradient-to-br from-red-100 to-rose-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">⚠️</span>
            </div>
            {/* Error title */}
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Error Loading Results</h2>
            {/* Error description */}
            <p className="text-gray-600 mb-8 text-lg">{error}</p>
            {/* Back to home button */}
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

        {/* Navigation buttons for new analysis, history, and refresh */}
        <div className="mb-8 flex gap-3">
          
          {/* New Analysis button */}
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

          {/* History page button */}
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

          {/* Refresh button, only active if query is processing */}
          <button
            onClick={fetchQueryData}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700
                       text-white font-medium py-2.5 px-5 rounded-xl
                       shadow-md hover:shadow-lg transition-all duration-200
                       disabled:opacity-50 disabled:cursor-not-allowed
                       flex items-center gap-2"
            disabled={queryData?.status !== 'processing'}
          >
            {/* Spinner icon if processing */}
            <span className={queryData?.status === 'processing' ? 'animate-spin' : ''}>🔄</span>
            Refresh
          </button>
        </div>

        {/* Display query results */}
        <ResultsDisplay queryData={queryData} />
      </div>
    </div>
  );
}
