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

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Pricing Comparison</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="company" />
          <YAxis label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }} />
          <Tooltip formatter={(value) => `$${value}`} />
          <Legend />
          <Bar dataKey="price" fill="#3b82f6" name="Monthly Price" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PricingChart;