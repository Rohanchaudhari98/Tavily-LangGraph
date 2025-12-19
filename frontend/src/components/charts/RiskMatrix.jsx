import React from 'react';

const RiskScoreCards = ({ data }) => {
    console.log(data);
  if (!data || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No risk data available
      </div>
    );
  }

  // Calculate risk level and color based on severity
  const getRiskLevel = (severity) => {
    if (severity >= 70) return { level: 'Critical', color: '#ef4444', bgColor: 'bg-red-50', borderColor: 'border-red-200', textColor: 'text-red-700' };
    if (severity >= 40) return { level: 'High', color: '#f97316', bgColor: 'bg-orange-50', borderColor: 'border-orange-200', textColor: 'text-orange-700' };
    if (severity >= 20) return { level: 'Medium', color: '#eab308', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-200', textColor: 'text-yellow-700' };
    return { level: 'Low', color: '#22c55e', bgColor: 'bg-green-50', borderColor: 'border-green-200', textColor: 'text-green-700' };
  };

  // Group data by risk type
  const groupedByRisk = {};
  data.forEach((item) => {
    const riskType = item.risk;
    if (!groupedByRisk[riskType]) {
      groupedByRisk[riskType] = [];
    }
    groupedByRisk[riskType].push(item);
  });

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Risk Assessment</h3>
      
      <div className="grid grid-cols-1 gap-6">
        {Object.entries(groupedByRisk).map(([riskType, companies], index) => {
          // Determine overall risk level for this risk type (use highest severity)
          const maxSeverity = Math.max(...companies.map(c => c.impact * c.likelihood));
          const riskInfo = getRiskLevel(maxSeverity);
          
          return (
            <div 
              key={index} 
              className={`border-2 rounded-lg p-6 ${riskInfo.borderColor} ${riskInfo.bgColor}`}
            >
              {/* Risk Type Header */}
              <div className="flex items-start justify-between mb-6">
                <h4 className="text-xl font-bold text-gray-900">{riskType}</h4>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${riskInfo.textColor} bg-white border ${riskInfo.borderColor}`}>
                  {riskInfo.level}
                </span>
              </div>

              {/* Company Comparisons */}
              <div className="space-y-6">
                {companies.map((company, idx) => {
                  const severity = company.impact * company.likelihood;
                  const companyRiskInfo = getRiskLevel(severity);
                  
                  return (
                    <div key={idx} className="bg-white rounded-lg p-4 border border-gray-200">
                      {/* Company Name */}
                      <div className="flex items-center justify-between mb-3">
                        <h5 className="text-lg font-semibold text-gray-800">
                          {company.company}
                        </h5>
                        <span className={`text-xl font-bold ${companyRiskInfo.textColor}`}>
                          {severity.toFixed(1)}
                        </span>
                      </div>

                      {/* Impact and Likelihood Bars */}
                      <div className="space-y-3">
                        {/* Impact */}
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-600 w-24">Impact</span>
                          <div className="flex items-center gap-2 flex-1">
                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div 
                                style={{ 
                                  width: `${(company.impact / 10) * 100}%`,
                                  backgroundColor: companyRiskInfo.color
                                }}
                                className="h-full"
                              ></div>
                            </div>
                            <span className="text-sm font-bold text-gray-900 w-6 text-right">{company.impact}</span>
                          </div>
                        </div>

                        {/* Likelihood */}
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-600 w-24">Likelihood</span>
                          <div className="flex items-center gap-2 flex-1">
                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div 
                                style={{ 
                                  width: `${(company.likelihood / 10) * 100}%`,
                                  backgroundColor: companyRiskInfo.color
                                }}
                                className="h-full"
                              ></div>
                            </div>
                            <span className="text-sm font-bold text-gray-900 w-6 text-right">{company.likelihood}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex justify-center gap-6 mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <span className="text-xs text-gray-600">Critical (70+)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
          <span className="text-xs text-gray-600">High (40-69)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <span className="text-xs text-gray-600">Medium (20-39)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-xs text-gray-600">Low (&lt;20)</span>
        </div>
      </div>
    </div>
  );
};

export default RiskScoreCards;