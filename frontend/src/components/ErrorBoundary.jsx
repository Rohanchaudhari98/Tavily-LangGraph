// Error boundary component to catch and display runtime errors in the UI

import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  // Update state when an error is caught
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  // Capture error details
  componentDidCatch(error, errorInfo) {
    // Log error to console
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Store error details in state
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Optional: send error to a reporting service like Sentry
  }

  render() {
    if (this.state.hasError) {
      // Fallback UI when an error occurs
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
            {/* Warning icon */}
            <div className="w-20 h-20 bg-gradient-to-br from-red-100 to-rose-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">⚠️</span>
            </div>

            {/* Error message */}
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-6">
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>

            {/* Optional error details */}
            {this.props.showDetails && this.state.error && (
              <details className="mt-4 text-left bg-gray-50 p-4 rounded-lg">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 mb-2">
                  Error Details
                </summary>
                <pre className="text-xs text-red-600 overflow-auto max-h-48">
                  {this.state.error.toString()}
                  {this.state.errorInfo && (
                    <div className="mt-2 text-gray-600">
                      {this.state.errorInfo.componentStack}
                    </div>
                  )}
                </pre>
              </details>
            )}

            {/* Action buttons */}
            <div className="flex gap-3 justify-center mt-6">
              <button
                onClick={() => window.location.reload()}
                className="btn-primary"
              >
                Refresh Page
              </button>
              <button
                onClick={() => (window.location.href = '/')}
                className="btn-secondary"
              >
                Go Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    // Render children if no error
    return this.props.children;
  }
}

export default ErrorBoundary;
