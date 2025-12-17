import QueryForm from '../components/QueryForm';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section with Gradient */}
      <div className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700"></div>
        
        {/* Decorative blobs */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-1000"></div>
        
        {/* Content */}
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6 leading-tight">
            Competitive Intelligence
            <span className="block text-blue-200">Made Simple</span>
          </h1>
          <p className="text-xl md:text-2xl text-blue-100 max-w-3xl mx-auto mb-8 leading-relaxed">
            Analyze your competitors using AI-powered research agents. Get comprehensive 
            insights on pricing, features, and market positioning in minutes.
          </p>
          
          {/* Quick stats */}
          <div className="flex justify-center gap-8 text-white mb-12">
            <div className="text-center">
              <div className="text-4xl font-bold mb-1">4</div>
              <div className="text-blue-200 text-sm">AI Agents</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold mb-1">⚡</div>
              <div className="text-blue-200 text-sm">Fast Results</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold mb-1">📊</div>
              <div className="text-blue-200 text-sm">Export Reports</div>
            </div>
          </div>
          
          <a href="#form" className="inline-block btn-primary text-lg">
            Start Your Analysis →
          </a>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16" id="form">
        {/* Query Form */}
        <div className="mb-20">
          <QueryForm />
        </div>

        {/* Features Section */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">Why Choose Us</h2>
            <p className="text-gray-600 text-lg">Powerful Features</p>
            <div className="h-1 w-20 bg-gradient-to-r from-blue-600 to-indigo-600 mx-auto mt-4 rounded-full"></div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="feature-card group">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="text-3xl">🤖</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                AI-Powered Research
              </h3>
              <p className="text-gray-600 leading-relaxed">
                4 specialized agents work together to gather comprehensive intelligence from multiple sources, ensuring thorough and accurate analysis.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="feature-card group">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="text-3xl">📊</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Deep Analysis
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Detailed insights on pricing strategies, product features, and market positioning with actionable recommendations.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="feature-card group">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="text-3xl">📄</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Export Reports
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Download comprehensive reports as PDF or Word documents, perfectly formatted for easy sharing with your team.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}