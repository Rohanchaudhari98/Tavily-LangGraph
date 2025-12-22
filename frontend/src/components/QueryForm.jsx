// Form component to create a competitor analysis query

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createQuery } from '../services/api';
import CompetitorInput from './CompetitorInput';

export default function QueryForm() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    company_name: '',
    query: '',
    use_premium_analysis: false,
  });

  const [competitors, setCompetitors] = useState([]);

  // Auto-discovery state
  const [useAutoDiscovery, setUseAutoDiscovery] = useState(false);
  const [maxCompetitors, setMaxCompetitors] = useState(5);

  // Freshness filter state
  const [freshness, setFreshness] = useState('anytime');

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation: Require competitors or auto-discovery
    if (!useAutoDiscovery && competitors.length === 0) {
      alert('Please add at least one competitor or enable auto-discovery');
      return;
    }

    setLoading(true);

    try {
      const requestData = {
        ...formData,
        competitors: useAutoDiscovery ? [] : competitors,
        use_auto_discovery: useAutoDiscovery,
        max_competitors: maxCompetitors,
        freshness: freshness,
      };

      const response = await createQuery(requestData);
      navigate(`/results/${response.query_id}`);
    } catch (error) {
      console.error('Failed to create query:', error);
      alert('Failed to submit query. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="space-y-5">

        {/* Company Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Your Company Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            required
            value={formData.company_name}
            onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
            placeholder="e.g., Tavily AI"
            className="input-field"
          />
        </div>

        {/* Query */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            What would you like to analyze? <span className="text-red-500">*</span>
          </label>
          <textarea
            required
            value={formData.query}
            onChange={(e) => setFormData({ ...formData, query: e.target.value })}
            placeholder="e.g., pricing strategy, product features, market positioning"
            rows={3}
            className="input-field"
          />
          <p className="text-xs text-gray-500 mt-1">
            Be specific about what aspects you want to compare
          </p>
        </div>

        {/* Freshness Filter */}
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border-2 border-green-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Freshness Filter</h3>
              <p className="text-sm text-gray-600">Filter search results by time range</p>
            </div>
          </div>

          <label className="block text-sm font-medium text-gray-700 mb-2">
            Time Range
          </label>
          <select
            value={freshness}
            onChange={(e) => setFreshness(e.target.value)}
            className="input-field w-full"
          >
            <option value="anytime">Anytime (All results)</option>
            <option value="1month">Past Month</option>
            <option value="3months">Past 3 Months</option>
            <option value="6months">Past 6 Months</option>
            <option value="1year">Past Year</option>
          </select>
          <p className="text-xs text-gray-500 mt-2">
            Newer results may be more relevant for rapidly changing markets
          </p>
        </div>

        {/* Auto-Discovery Toggle */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Auto-Discovery</h3>
                <p className="text-sm text-gray-600">Let AI find competitors automatically</p>
              </div>
            </div>

            {/* Toggle Switch */}
            <button
              type="button"
              onClick={() => setUseAutoDiscovery(!useAutoDiscovery)}
              className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors
                ${useAutoDiscovery 
                  ? 'bg-gradient-to-br from-gray-900 via-indigo-900 to-purple-900' 
                  : 'bg-gray-300'
                }`}
            >
              <span
                className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                  useAutoDiscovery ? 'translate-x-7' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Max Competitors Selector - Only show when auto-discovery is ON */}
          {useAutoDiscovery && (
            <div className="mt-4 pt-4 border-t border-blue-200">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Competitors to Find
              </label>
              <select
                value={maxCompetitors}
                onChange={(e) => setMaxCompetitors(Number(e.target.value))}
                className="input-field w-full"
              >
                <option value={3}>3 Competitors</option>
                <option value={5}>5 Competitors</option>
                <option value={7}>7 Competitors</option>
                <option value={10}>10 Competitors</option>
              </select>
              <p className="text-xs text-gray-500 mt-2">
                AI will search the web and identify the most relevant competitors
              </p>
            </div>
          )}
        </div>

        {/* Competitors - Only show when auto-discovery is OFF */}
        {!useAutoDiscovery && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Competitor Companies <span className="text-red-500">*</span>
            </label>
            <CompetitorInput competitors={competitors} setCompetitors={setCompetitors} />
          </div>
        )}

        {/* Premium Analysis Toggle */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <label className="flex items-start cursor-pointer">
            <input
              type="checkbox"
              checked={formData.use_premium_analysis}
              onChange={(e) => setFormData({ ...formData, use_premium_analysis: e.target.checked })}
              className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <div className="ml-3">
              <span className="text-sm font-medium text-gray-900">Premium Analysis</span>
              <p className="text-xs text-gray-600 mt-0.5">
                Uses GPT-4o for higher quality insights (takes longer, costs more)
              </p>
            </div>
          </label>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          <button
            type="submit"
            disabled={loading || (!useAutoDiscovery && competitors.length === 0)}
            className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Submitting...' : 'Analyze Competitors'}
          </button>

          <button
            type="button"
            onClick={() => navigate('/history')}
            className="btn-secondary"
          >
            History
          </button>
        </div>

        {/* Time Estimate */}
        {!loading && (
          <p className="text-center text-sm text-gray-500">
            ⏱️ {useAutoDiscovery 
              ? `Estimated time: ${maxCompetitors * 6}-${maxCompetitors * 8} seconds (includes discovery)`
              : competitors.length > 0 
                ? `Estimated time: ${competitors.length * 5}-${competitors.length * 7} seconds`
                : 'Add competitors or enable auto-discovery to see time estimate'
            }
          </p>
        )}
      </div>
    </form>
  );
}
