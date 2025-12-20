// Displays all available charts (pricing, features, risk) for a query

import React from 'react';
import PricingChart from './PricingChart';
import FeatureRadar from './FeatureRadar';
import RiskMatrix from './RiskMatrix';

const ChartsView = ({ chartData }) => {
  if (!chartData) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Chart Data Available</h3>
        <p className="text-gray-500">
          Chart visualizations will appear here once the analysis is complete.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Pricing Chart */}
      {chartData.pricing && chartData.pricing.length > 0 && <PricingChart data={chartData.pricing} />}

      {/* Feature Radar */}
      {chartData.features && chartData.features.length > 0 && <FeatureRadar data={chartData.features} />}

      {/* Risk Matrix */}
      {chartData.risks && chartData.risks.length > 0 && <RiskMatrix data={chartData.risks} />}

      {/* Fallback if no charts available */}
      {(!chartData.pricing || chartData.pricing.length === 0) &&
       (!chartData.features || chartData.features.length === 0) &&
       (!chartData.risks || chartData.risks.length === 0) && (
        <div className="text-center text-gray-500 py-8">
          No chart data could be extracted from the analysis.
        </div>
      )}
    </div>
  );
};

export default ChartsView;
