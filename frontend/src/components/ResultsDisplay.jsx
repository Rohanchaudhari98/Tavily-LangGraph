// Displays query results with analysis, charts, research, and metadata

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ExportButtons from './ExportButtons';
import ChartsView from './charts/ChartsView';
import AgentProgress from './AgentProgress';

export default function ResultsDisplay({ queryData }) {
  const [activeTab, setActiveTab] = useState('analysis');
  const [activeSubTab, setActiveSubTab] = useState('narrative');

  // Show message if no data
  if (!queryData) {
    return (
      <div className="card p-12 text-center">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  const totalAgents = queryData.total_agents || (queryData.use_auto_discovery ? 5 : 4);
  const completedAgentsCount = queryData.completed_agents?.length || 0;

  // Format freshness for display
  const formatFreshness = (freshness) => {
    const freshnessMap = {
      anytime: 'Anytime (All results)',
      '1month': 'Past Month',
      '3months': 'Past 3 Months',
      '6months': 'Past 6 Months',
      '1year': 'Past Year'
    };
    return freshnessMap[freshness] || 'Anytime';
  };

  // Render status badge
  const renderStatus = () => {
    const statusConfig = {
      processing: { className: 'status-badge-processing', icon: '⏳', label: 'Processing', animate: true },
      completed: { className: 'status-badge-completed', icon: '✓', label: 'Completed', animate: false },
      failed: { className: 'status-badge-failed', icon: '✗', label: 'Failed', animate: false },
    };
    const config = statusConfig[queryData.status] || statusConfig.completed;

    return (
      <span className={config.className}>
        <span className={config.animate ? 'animate-pulse mr-1.5' : 'mr-1.5'}>{config.icon}</span>
        {config.label}
      </span>
    );
  };

  const tabs = [
    { id: 'analysis', label: 'Analysis', show: queryData.status === 'completed' },
    { id: 'research', label: 'Research Results', show: queryData.research_results?.length > 0 },
    { id: 'metadata', label: 'Metadata', show: true },
  ];

  const subTabs = [
    { id: 'narrative', label: 'Narrative', icon: '📄' },
    { id: 'charts', label: 'Charts', icon: '📈' },
  ];

  return (
    <div className="space-y-8">
      {/* Header / Hero Card */}
      <div className="relative overflow-hidden rounded-2xl">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-indigo-900 to-purple-900"></div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-700 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
        <div className="relative p-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <h2 className="text-3xl font-extrabold text-white mb-2">{queryData.company_name}</h2>
              <p className="text-xl text-blue-100 leading-relaxed">{queryData.query}</p>
            </div>
            {renderStatus()}
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-4 text-center hover:bg-white/15 transition-all">
              <div className="text-white/80 text-sm mb-1">Competitors</div>
              <div className="text-3xl font-bold text-white">{queryData.competitors.length}</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-4 text-center hover:bg-white/15 transition-all">
              <div className="text-white/80 text-sm mb-1">Created</div>
              <div className="text-lg font-semibold text-white">
                {new Date(queryData.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-4 text-center hover:bg-white/15 transition-all">
              <div className="text-white/80 text-sm mb-1">Mode</div>
              <div className="text-lg font-semibold text-white">
                {queryData.analysis_mode === 'premium' ? '⭐ Premium' : 'Standard'}
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-4 text-center hover:bg-white/15 transition-all">
              <div className="text-white/80 text-sm mb-1">Progress</div>
              <div className="text-lg font-semibold text-white">{completedAgentsCount}/{totalAgents} agents</div>
            </div>
          </div>

          {/* Export Section */}
          {queryData.status === 'completed' && (
            <div className="mt-6 pt-6 border-t border-white/20">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <span>📥</span>
                  Export Report
                </h3>
                <ExportButtons queryData={queryData} />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Agent Progress & Flow Visualization */}
      {(queryData.status === 'processing' || queryData.status === 'completed') && (
        <div className="card p-8">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <span>🤝</span>
            Agent Collaboration Flow
          </h3>
          
          {/* Agent Progress Component */}
          <AgentProgress completed={queryData.completed_agents || []} />
          
          {/* Visual Flow Diagram */}
          <div className="mt-6 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
              <span>📊</span>
              Complete Query-to-Result Flow
            </h4>
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="px-3 py-1.5 bg-white rounded-lg border border-gray-300 font-medium text-gray-700">
                1. Query Submitted
              </span>
              <span className="text-gray-400">→</span>
              {queryData.use_auto_discovery && (
                <>
                  <span className={`px-3 py-1.5 rounded-lg border font-medium ${
                    queryData.completed_agents?.includes('competitor_discovery') || queryData.completed_agents?.includes('discovery')
                      ? 'bg-green-100 border-green-300 text-green-700'
                      : 'bg-gray-100 border-gray-300 text-gray-500'
                  }`}>
                    2. Discovery Agent
                  </span>
                  <span className="text-gray-400">→</span>
                </>
              )}
              <span className={`px-3 py-1.5 rounded-lg border font-medium ${
                queryData.completed_agents?.includes('research')
                  ? 'bg-green-100 border-green-300 text-green-700'
                  : 'bg-gray-100 border-gray-300 text-gray-500'
              }`}>
                {queryData.use_auto_discovery ? '3. Research Agent' : '2. Research Agent'}
              </span>
              <span className="text-gray-400">→</span>
              <span className={`px-3 py-1.5 rounded-lg border font-medium ${
                queryData.completed_agents?.includes('extraction')
                  ? 'bg-green-100 border-green-300 text-green-700'
                  : 'bg-gray-100 border-gray-300 text-gray-500'
              }`}>
                {queryData.use_auto_discovery ? '4. Extraction Agent' : '3. Extraction Agent'}
              </span>
              <span className="text-gray-400">→</span>
              <span className={`px-3 py-1.5 rounded-lg border font-medium ${
                queryData.completed_agents?.includes('crawl')
                  ? 'bg-green-100 border-green-300 text-green-700'
                  : 'bg-gray-100 border-gray-300 text-gray-500'
              }`}>
                {queryData.use_auto_discovery ? '5. Crawl Agent' : '4. Crawl Agent'}
              </span>
              <span className="text-gray-400">→</span>
              <span className={`px-3 py-1.5 rounded-lg border font-medium ${
                queryData.completed_agents?.includes('analysis')
                  ? 'bg-green-100 border-green-300 text-green-700'
                  : 'bg-gray-100 border-gray-300 text-gray-500'
              }`}>
                {queryData.use_auto_discovery ? '6. Analysis Agent' : '5. Analysis Agent'}
              </span>
              <span className="text-gray-400">→</span>
              <span className={`px-3 py-1.5 rounded-lg border font-medium ${
                queryData.status === 'completed'
                  ? 'bg-green-100 border-green-300 text-green-700'
                  : 'bg-gray-100 border-gray-300 text-gray-500'
              }`}>
                Final Report
              </span>
            </div>
            
            {/* Agent Collaboration Explanation */}
            {queryData.status === 'processing' && (
              <div className="mt-4 p-4 bg-white/60 rounded-lg border border-blue-200">
                <p className="text-xs text-gray-600 leading-relaxed">
                  <strong className="text-gray-700">How Agents Collaborate:</strong> Each agent builds on the previous agent's work. 
                  The Discovery Agent finds competitors, Research Agent searches the web, Extraction Agent pulls structured data, 
                  Crawl Agent does deep analysis, and Analysis Agent synthesizes everything into the final report.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Analysis Tabs Card */}
      <div className="card p-8">
        {/* Main Tabs */}
        <div className="border-b-2 border-gray-200 mb-8">
          <nav className="flex space-x-8 -mb-px">
            {tabs.filter(tab => tab.show).map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-4 px-2 border-b-4 font-semibold text-sm transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-700 border-b-4 border-transparent'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div>
          {/* Analysis Tab */}
          {activeTab === 'analysis' && (
            <div>
              {queryData.status === 'completed' && queryData.analysis ? (
                <div>
                  {/* Sub-tabs */}
                  <div className="flex space-x-1 mb-6 border-b border-gray-200">
                    {subTabs.map(tab => (
                      <button
                        key={tab.id}
                        onClick={() => setActiveSubTab(tab.id)}
                        className={`px-4 py-2 text-sm font-medium transition-colors ${
                          activeSubTab === tab.id
                            ? 'text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-700 border-b-2 border-transparent font-semibold'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                      >
                        <span className="mr-2">{tab.icon}</span>
                        {tab.label}
                      </button>
                    ))}
                  </div>

                  {/* Narrative Section */}
                  {activeSubTab === 'narrative' && (
                    <div className="prose prose-lg max-w-none overflow-x-auto bg-white/5 p-6 rounded-xl shadow-sm">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mt-6 mb-4" {...props} />,
                          h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mt-5 mb-3" {...props} />,
                          h3: ({ node, ...props }) => <h3 className="text-lg font-semibold mt-4 mb-2" {...props} />,
                          p: ({ node, ...props }) => <p className="leading-relaxed mb-4" {...props} />,
                          li: ({ node, ...props }) => <li className="mb-2 ml-4 list-disc" {...props} />,
                          code: ({ node, ...props }) => (
                            <code className="bg-gray-200 text-gray-800 rounded px-1 py-0.5 text-sm" {...props} />
                          ),
                          table: ({ node, ...props }) => (
                            <div className="overflow-x-auto my-4">
                              <table className="table-auto border-collapse border border-gray-300 w-full" {...props} />
                            </div>
                          ),
                          th: ({ node, ...props }) => <th className="border border-gray-300 bg-gray-100 px-3 py-1 text-left" {...props} />,
                          td: ({ node, ...props }) => <td className="border border-gray-300 px-3 py-1" {...props} />,
                        }}
                      >
                        {queryData.analysis}
                      </ReactMarkdown>
                    </div>
                  )}

                  {/* Charts Section */}
                  {activeSubTab === 'charts' && <ChartsView chartData={queryData.chart_data} />}
                </div>
              ) : queryData.status === 'processing' ? (
                // Processing UI
                <div className="text-center py-16">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Analysis in progress...</h3>
                  <p className="text-gray-600 mb-4">
                    This usually takes {queryData.use_auto_discovery ? '30-40' : '20-30'} seconds
                  </p>
                  <div className="inline-flex items-center gap-2 text-sm text-gray-500 bg-gray-100 px-4 py-2 rounded-full">
                    <span>✓</span>
                    <span>Completed: {queryData.completed_agents?.join(', ') || 'none'}</span>
                  </div>
                </div>
              ) : (
                // Failed / unavailable
                <div className="text-center py-16">
                  <div className="w-20 h-20 bg-gradient-to-br from-red-100 to-rose-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-4xl">⚠️</span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Analysis not available</h3>
                  {queryData.errors?.length > 0 && (
                    <div className="mt-6 p-6 bg-red-50 border-2 border-red-200 rounded-xl max-w-2xl mx-auto">
                      <p className="text-red-800 font-semibold mb-2">Errors:</p>
                      {queryData.errors.map((error, i) => (
                        <p key={i} className="text-red-700 text-sm mt-1">{error}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Research Tab */}
          {activeTab === 'research' && (
            <div className="space-y-6">
              {queryData.research_results?.map((result, index) => (
                <div key={index} className="bg-gradient-to-br from-white to-gray-50 border-2 border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all">
                  <h3 className="font-bold text-xl text-gray-900 mb-4 flex items-center gap-2">
                    <span className="text-blue-600">🎯</span>
                    {result.competitor}
                  </h3>
                  {result.status === 'success' ? (
                    <>
                      {result.answer && (
                        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                          <p className="text-sm font-semibold text-blue-900 mb-2">AI Summary:</p>
                          <p className="text-gray-700 leading-relaxed">{result.answer}</p>
                        </div>
                      )}
                      {result.results?.length > 0 && (
                        <div>
                          <p className="text-sm font-semibold text-gray-700 mb-3">📚 Sources:</p>
                          <ul className="space-y-2">
                            {result.results.slice(0, 3).map((source, i) => (
                              <li key={i}>
                                <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 font-medium hover:underline flex items-start gap-2">
                                  <span className="text-gray-400 mt-1">→</span>
                                  <span>{source.title}</span>
                                </a>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-red-700 font-medium">❌ Failed: {result.error}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Metadata Tab */}
          {activeTab === 'metadata' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-6">
                <h3 className="font-bold text-lg text-gray-900 mb-4 flex items-center gap-2">
                  <span>📋</span>
                  Query Details
                </h3>
                <dl className="grid grid-cols-1 gap-4">
                  <div className="flex justify-between items-center py-2 border-b border-blue-200">
                    <dt className="text-sm font-medium text-gray-600">Query ID:</dt>
                    <dd className="text-sm font-mono text-gray-900 bg-white px-3 py-1 rounded">{queryData.query_id}</dd>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-blue-200">
                    <dt className="text-sm font-medium text-gray-600">Discovery Mode:</dt>
                    <dd className="text-sm font-semibold text-gray-900">{queryData.use_auto_discovery ? '🔍 Auto-Discovery' : '📋 Manual Entry'}</dd>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-blue-200">
                    <dt className="text-sm font-medium text-gray-600">Freshness Filter:</dt>
                    <dd className="text-sm font-semibold text-gray-900 flex items-center gap-2">
                      <span>🕒</span>
                      {formatFreshness(queryData.freshness || 'anytime')}
                    </dd>
                  </div>
                  <div className="flex justify-between items-start py-2 border-b border-blue-200">
                    <dt className="text-sm font-medium text-gray-600">Competitors:</dt>
                    <dd className="text-sm text-gray-900 text-right">{queryData.competitors.join(', ')}</dd>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-blue-200">
                    <dt className="text-sm font-medium text-gray-600">Created:</dt>
                    <dd className="text-sm text-gray-900">{new Date(queryData.created_at).toLocaleString()}</dd>
                  </div>
                  {queryData.completed_at && (
                    <div className="flex justify-between items-center py-2">
                      <dt className="text-sm font-medium text-gray-600">Completed:</dt>
                      <dd className="text-sm text-gray-900">{new Date(queryData.completed_at).toLocaleString()}</dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* Processing Details */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6">
                <h3 className="font-bold text-lg text-gray-900 mb-4 flex items-center gap-2">
                  <span>⚙️</span>
                  Processing Details
                </h3>
                <dl className="grid grid-cols-1 gap-4">
                  <div className="flex justify-between items-center py-2 border-b border-green-200">
                    <dt className="text-sm font-medium text-gray-600">Total Agents:</dt>
                    <dd className="text-sm font-semibold text-gray-900">{totalAgents}</dd>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-green-200">
                    <dt className="text-sm font-medium text-gray-600">Completed Agents:</dt>
                    <dd className="text-sm font-semibold text-gray-900">{queryData.completed_agents?.join(', ') || 'None'}</dd>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-green-200">
                    <dt className="text-sm font-medium text-gray-600">Analysis Mode:</dt>
                    <dd className="text-sm font-semibold text-gray-900">{queryData.analysis_mode || 'standard'}</dd>
                  </div>
                  {queryData.errors?.length > 0 && (
                    <div className="py-2">
                      <dt className="text-sm font-medium text-gray-600 mb-2">Errors:</dt>
                      <dd className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">{queryData.errors.join(', ')}</dd>
                    </div>
                  )}
                </dl>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
