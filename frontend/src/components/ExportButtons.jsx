// Component providing buttons to export query data as PDF or Word

import { exportToPDF, exportToWord } from '../services/exportService';
import { useState } from 'react';

export default function ExportButtons({ queryData }) {
  const [exporting, setExporting] = useState(null);

  // Trigger PDF export
  const handleExportPDF = async () => {
    setExporting('pdf');
    try {
      exportToPDF(queryData);
    } catch (error) {
      console.error('PDF export failed:', error);
      alert('Failed to export PDF. Please try again.');
    } finally {
      setExporting(null);
    }
  };

  // Trigger Word export
  const handleExportWord = async () => {
    setExporting('word');
    try {
      await exportToWord(queryData);
    } catch (error) {
      console.error('Word export failed:', error);
      alert('Failed to export Word document. Please try again.');
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className="flex gap-3">
      {/* PDF Export Button */}
      <button
        onClick={handleExportPDF}
        disabled={exporting !== null}
        className="bg-white hover:bg-gray-50 text-blue-600 font-semibold py-2.5 px-5
                   rounded-xl border-2 border-blue-200 hover:border-blue-300
                   shadow-md hover:shadow-lg transition-all duration-200
                   disabled:opacity-50 disabled:cursor-not-allowed
                   flex items-center gap-2"
      >
        {exporting === 'pdf' ? (
          <>
            {/* Loading spinner */}
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
            <span>Exporting...</span>
          </>
        ) : (
          <>
            <span className="text-lg">📄</span>
            <span>PDF</span>
          </>
        )}
      </button>

      {/* Word Export Button */}
      <button
        onClick={handleExportWord}
        disabled={exporting !== null}
        className="bg-white hover:bg-gray-50 text-indigo-600 font-semibold py-2.5 px-5
                   rounded-xl border-2 border-indigo-200 hover:border-indigo-300
                   shadow-md hover:shadow-lg transition-all duration-200
                   disabled:opacity-50 disabled:cursor-not-allowed
                   flex items-center gap-2"
      >
        {exporting === 'word' ? (
          <>
            {/* Loading spinner */}
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-indigo-600 border-t-transparent"></div>
            <span>Exporting...</span>
          </>
        ) : (
          <>
            <span className="text-lg">📝</span>
            <span>Word</span>
          </>
        )}
      </button>
    </div>
  );
}
