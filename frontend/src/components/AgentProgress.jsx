// Component to display the progress of different agents
const AGENTS = [
  { key: 'discovery', label: 'Discovery' },
  { key: 'research', label: 'Research' },
  { key: 'extraction', label: 'Extraction' },
  { key: 'crawl', label: 'Crawl' },
  { key: 'analysis', label: 'Analysis' }
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
          // Completion state for this agent
          const done = completed.includes(agent.key);

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
