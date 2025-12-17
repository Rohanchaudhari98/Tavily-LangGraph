import { useState } from 'react';

export default function CompetitorInput({ competitors, setCompetitors }) {
  const [inputValue, setInputValue] = useState('');

  const addCompetitor = () => {
    if (inputValue.trim() && competitors.length < 10) {
      setCompetitors([...competitors, inputValue.trim()]);
      setInputValue('');
    }
  };

  const removeCompetitor = (index) => {
    setCompetitors(competitors.filter((_, i) => i !== index));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addCompetitor();
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Competitors (Max 10)
      </label>
      
      {/* List of added competitors */}
      <div className="space-y-2 mb-3">
        {competitors.map((competitor, index) => (
          <div
            key={index}
            className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-lg"
          >
            <span className="text-gray-700">{competitor}</span>
            <button
              type="button"
              onClick={() => removeCompetitor(index)}
              className="text-red-600 hover:text-red-800 font-medium"
            >
              Remove
            </button>
          </div>
        ))}
      </div>

      {/* Add competitor input */}
      {competitors.length < 10 && (
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter competitor name"
            className="input-field flex-1"
          />
          <button
            type="button"
            onClick={addCompetitor}
            className="btn-secondary whitespace-nowrap"
            disabled={!inputValue.trim()}
          >
            Add
          </button>
        </div>
      )}

      {competitors.length === 0 && (
        <p className="text-sm text-red-600 mt-2">
          Please add at least one competitor
        </p>
      )}
    </div>
  );
}