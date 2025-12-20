// Component showing a loading spinner with an optional message

export default function LoadingSpinner({ message = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      {/* Spinner animation */}
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>

      {/* Loading message */}
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
}
