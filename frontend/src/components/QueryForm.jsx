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

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (competitors.length === 0) {
      alert('Please add at least one competitor');
      return;
    }

    setLoading(true);

    try {
      const requestData = {
        ...formData,
        competitors,
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
            placeholder="e.g., Tavily"
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

        {/* Competitors */}
        <CompetitorInput competitors={competitors} setCompetitors={setCompetitors} />

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
            disabled={loading || competitors.length === 0}
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

        {competitors.length > 0 && !loading && (
          <p className="text-center text-sm text-gray-500">
            ⏱️ Estimated time: {competitors.length * 5}-{competitors.length * 7} seconds
          </p>
        )}
      </div>
    </form>
  );
}