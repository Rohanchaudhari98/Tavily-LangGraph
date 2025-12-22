// Page to display results of a specific query
// Handles loading, error states, smart polling, and frontend completion fix

import { useState, useEffect, useRef } from 'react';
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
  const [isFetching, setIsFetching] = useState(false);
  const statusRef = useRef(null);

  // Helper to merge new data with existing queryData
  const mergeQueryData = (newData) => {
    setQueryData((prev) => {
      if (!prev) return newData;
      return {
        ...prev,
        ...newData,
        completed_agents: Array.from(new Set([...(prev.completed_agents || []), ...(newData.completed_agents || [])])),
      };
    });
  };

  useEffect(() => {
    let isMounted = true;
    let delay = 3000;

    const pollQuery = async () => {
      if (!isMounted || isFetching) return;

      setIsFetching(true);
      try {
        const data = await getQuery(queryId);
        if (!isMounted) return;

        // Frontend-only completion fix
        if (data.analysis && !(data.completed_agents || []).includes('analysis')) {
          data.completed_agents = [...(data.completed_agents || []), 'analysis'];
        }
        if (data.analysis && data.status !== 'completed') {
          data.status = 'completed';
          if (!data.completed_agents.includes('final_report')) {
            data.completed_agents.push('final_report');
          }
        }

        mergeQueryData(data);
        statusRef.current = data?.status;
        setLoading(false);
        setError(null);

        // Only poll again if still processing
        if (data?.status === 'processing') {
          delay = Math.min(delay * 1.5, 15000);
          setTimeout(pollQuery, delay);
        }
      } catch (err) {
        console.error('Failed to fetch query:', err);
        if (!isMounted) return;
        setError('Failed to load query results');
        setLoading(false);
      } finally {
        setIsFetching(false);
      }
    };

    pollQuery();

    return () => {
      isMounted = false;
    };
  }, [queryId]);

  const handleManualRefresh = async () => {
    if (isFetching) return;
    setIsFetching(true);
    try {
      const data = await getQuery(queryId);

      // Same frontend completion fix for manual refresh
      if (data.analysis && !(data.completed_agents || []).includes('analysis')) {
        data.completed_agents = [...(data.completed_agents || []), 'analysis'];
      }
      if (data.analysis && data.status !== 'completed') {
        data.status = 'completed';
        if (!data.completed_agents.includes('final_report')) {
          data.completed_agents.push('final_report');
        }
      }

      mergeQueryData(data);
      statusRef.current = data?.status;
      setError(null);
    } catch (err) {
      console.error('Manual refresh failed:', err);
      setError('Failed to refresh query results');
    } finally {
      setIsFetching(false);
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
        {/* Navigation buttons */}
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
            onClick={handleManualRefresh}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700
                       text-white font-medium py-2.5 px-5 rounded-xl
                       shadow-md hover:shadow-lg transition-all duration-200
                       disabled:opacity-50 disabled:cursor-not-allowed
                       flex items-center gap-2"
            disabled={queryData?.status !== 'processing' || isFetching}
          >
            <span className={queryData?.status === 'processing' && isFetching ? 'animate-spin' : ''}>
              🔄
            </span>
            Refresh
          </button>
        </div>

        {/* Display query results */}
        <ResultsDisplay queryData={queryData} />
      </div>
    </div>
  );
}
