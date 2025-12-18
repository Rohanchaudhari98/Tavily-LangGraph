import React from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ResponsiveContainer, Tooltip } from 'recharts';

const FeatureRadar = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No feature data available
      </div>
    );
  }

  // Get all company names (exclude 'feature' key)
  const companies = Object.keys(data[0]).filter(key => key !== 'feature');
  
  // Color palette for different companies
  const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Comparison</h3>
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="feature" />
          <PolarRadiusAxis angle={90} domain={[0, 10]} />
          <Tooltip />
          <Legend />
          {companies.map((company, index) => (
            <Radar
              key={company}
              name={company}
              dataKey={company}
              stroke={colors[index % colors.length]}
              fill={colors[index % colors.length]}
              fillOpacity={0.3}
            />
          ))}
        </RadarChart>
      </ResponsiveContainer>
      <p className="text-sm text-gray-500 mt-2 text-center">
        Score: 0 (Lowest) to 10 (Highest)
      </p>
    </div>
  );
};

export default FeatureRadar;