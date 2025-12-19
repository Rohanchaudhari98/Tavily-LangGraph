import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PricingChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No pricing data available
      </div>
    );
  }

  const accentColors = ['#14B8A6', '#6366F1', '#9CA3AF']; // teal, indigo, soft gray

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Pricing Comparison</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          {/* Gradient definition */}
          <defs>
            <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2563EB" stopOpacity={0.9} />
              <stop offset="100%" stopColor="#2F80ED" stopOpacity={0.6} />
            </linearGradient>
          </defs>

          <CartesianGrid stroke="#E5E7EB" strokeDasharray="3 3" />
          <XAxis dataKey="company" stroke="#374151" tick={{ fontSize: 12 }} />
          <YAxis 
            label={{ value: 'Price ($)', angle: -90, position: 'insideLeft', fill: '#374151', fontSize: 12 }}
            stroke="#374151"
          />
          <Tooltip formatter={(value) => `$${value}`} />
          <Legend />

          {data[0] &&
            Object.keys(data[0])
              .filter(key => key !== 'company')
              .map((key, index) => (
                <Bar
                  key={key}
                  dataKey={key}
                  name={key}
                  fill={index === 0 ? 'url(#blueGradient)' : accentColors[(index - 1) % accentColors.length]}
                  radius={[4, 4, 0, 0]} // rounded top corners
                />
              ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PricingChart;
