import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ZAxis } from 'recharts';

const RiskMatrix = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No risk data available
      </div>
    );
  }

  // Color code by impact * likelihood
  const getColor = (impact, likelihood) => {
    const severity = impact * likelihood;
    if (severity >= 70) return '#ef4444'; // Red - Critical
    if (severity >= 40) return '#f59e0b'; // Orange - High
    return '#10b981'; // Green - Medium
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
          <p className="font-semibold text-gray-900">{data.risk}</p>
          <p className="text-sm text-gray-600">Impact: {data.impact}/10</p>
          <p className="text-sm text-gray-600">Likelihood: {data.likelihood}/10</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Matrix</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            type="number" 
            dataKey="likelihood" 
            name="Likelihood" 
            domain={[0, 10]}
            label={{ value: 'Likelihood', position: 'insideBottom', offset: -10 }}
          />
          <YAxis 
            type="number" 
            dataKey="impact" 
            name="Impact" 
            domain={[0, 10]}
            label={{ value: 'Impact', angle: -90, position: 'insideLeft' }}
          />
          <ZAxis range={[400, 400]} />
          <Tooltip content={<CustomTooltip />} />
          <Scatter name="Risks" data={data}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.impact, entry.likelihood)} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div className="flex justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <span className="text-gray-600">Critical Risk</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
          <span className="text-gray-600">High Risk</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-gray-600">Medium Risk</span>
        </div>
      </div>
    </div>
  );
};

export default RiskMatrix;