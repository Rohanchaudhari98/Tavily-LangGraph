// Component to display the progress of different agents
const AGENTS = [
  { key: 'competitor_discovery', altKey: 'discovery', label: 'Discovery', description: 'Finds competitors automatically' },
  { key: 'research', label: 'Research', description: 'Searches web for competitor info' },
  { key: 'extraction', label: 'Extraction', description: 'Extracts structured data' },
  { key: 'crawl', label: 'Crawl', description: 'Deep crawls competitor sites' },
  { key: 'analysis', label: 'Analysis', description: 'Synthesizes final report' }
];

export default function AgentProgress({ completed = [] }) {
  return (
    <div className="mb-6 bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
      {/* Header */}
      <h3 className="text-lg font-semibold mb-4">
        Agent Progress
      </h3>

      {/* Agent status list */}
      <div className="flex flex-wrap gap-3">
        {AGENTS.map((agent) => {
          // Completion state for this agent (check both key and altKey)
          const done = completed.includes(agent.key) || (agent.altKey && completed.includes(agent.altKey));

          return (
            <div
              key={agent.key}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg border
                text-sm font-medium
                ${
                  done
                    ? 'bg-green-50 border-green-300 text-green-700'
                    : 'bg-gray-50 border-gray-300 text-gray-400'
                }
              `}
              title={agent.description}
            >
              {/* Status icon */}
              <span>{done ? '✅' : '⏳'}</span>

              {/* Agent label */}
              {agent.label}
            </div>
          );
        })}
      </div>
    </div>
  );
}
