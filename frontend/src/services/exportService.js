import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { Document, Packer, Paragraph, TextRun, HeadingLevel } from 'docx';
import { saveAs } from 'file-saver';

/**
 * Export analysis to PDF with proper page breaks
 */
export const exportToPDF = (queryData) => {
  const doc = new jsPDF({
    format: 'a4',
    unit: 'mm',
  });
  
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;
  const maxLineWidth = pageWidth - (margin * 2);
  
  let yPosition = margin;
  
  // Helper function to add new page if needed
  const checkPageBreak = (requiredSpace) => {
    if (yPosition + requiredSpace > pageHeight - margin) {
      doc.addPage();
      yPosition = margin;
      return true;
    }
    return false;
  };
  
  // Title
  doc.setFontSize(24);
  doc.setFont(undefined, 'bold');
  doc.text('Competitive Intelligence Report', margin, yPosition);
  yPosition += 15;
  
  // Metadata section
  doc.setFontSize(11);
  doc.setFont(undefined, 'normal');
  
  const metadata = [
    `Company: ${queryData.company_name}`,
    `Query: ${queryData.query}`,
    `Competitors: ${queryData.competitors.join(', ')}`,
    `Generated: ${new Date(queryData.created_at).toLocaleString()}`,
    `Status: ${queryData.status}`
  ];
  
  metadata.forEach(line => {
    checkPageBreak(7);
    doc.text(line, margin, yPosition);
    yPosition += 7;
  });
  
  yPosition += 5;
  
  // Add separator line
  doc.setDrawColor(200, 200, 200);
  doc.line(margin, yPosition, pageWidth - margin, yPosition);
  yPosition += 10;
  
  // Analysis content
  if (queryData.analysis) {
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    checkPageBreak(10);
    doc.text('Analysis:', margin, yPosition);
    yPosition += 10;
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    
    // Split text into lines that fit the page width
    const lines = doc.splitTextToSize(queryData.analysis, maxLineWidth);
    
    lines.forEach((line) => {
      checkPageBreak(6);
      doc.text(line, margin, yPosition);
      yPosition += 6;
    });
  }
  
  // Save
  const filename = `${queryData.company_name}_analysis_${queryData.query_id}.pdf`;
  doc.save(filename);
};

/**
 * Export analysis to Word (.docx) - Enhanced version
 */
export const exportToWord = async (queryData) => {
  // Split analysis into sections
  const sections = queryData.analysis.split('\n').filter(line => line.trim());
  
  const children = [
    // Title
    new Paragraph({
      text: 'Competitive Intelligence Report',
      heading: HeadingLevel.HEADING_1,
      spacing: { after: 400 },
    }),
    
    // Metadata
    new Paragraph({
      children: [
        new TextRun({ text: 'Company: ', bold: true }),
        new TextRun(queryData.company_name),
      ],
      spacing: { after: 200 },
    }),
    
    new Paragraph({
      children: [
        new TextRun({ text: 'Query: ', bold: true }),
        new TextRun(queryData.query),
      ],
      spacing: { after: 200 },
    }),
    
    new Paragraph({
      children: [
        new TextRun({ text: 'Competitors: ', bold: true }),
        new TextRun(queryData.competitors.join(', ')),
      ],
      spacing: { after: 200 },
    }),
    
    new Paragraph({
      children: [
        new TextRun({ text: 'Generated: ', bold: true }),
        new TextRun(new Date(queryData.created_at).toLocaleString()),
      ],
      spacing: { after: 200 },
    }),
    
    new Paragraph({
      children: [
        new TextRun({ text: 'Status: ', bold: true }),
        new TextRun(queryData.status),
      ],
      spacing: { after: 400 },
    }),
    
    // Analysis heading
    new Paragraph({
      text: 'Analysis',
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 400, after: 200 },
    }),
  ];
  
  // Add analysis content with proper formatting
  sections.forEach((line) => {
    if (line.startsWith('# ')) {
      // Main heading
      children.push(new Paragraph({
        text: line.substring(2),
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 400, after: 200 },
      }));
    } else if (line.startsWith('## ')) {
      // Sub heading
      children.push(new Paragraph({
        text: line.substring(3),
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 300, after: 150 },
      }));
    } else if (line.startsWith('### ')) {
      // Sub-sub heading
      children.push(new Paragraph({
        text: line.substring(4),
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 200, after: 100 },
      }));
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      // Bullet point
      children.push(new Paragraph({
        text: line.substring(2),
        bullet: {
          level: 0
        },
        spacing: { after: 100 },
      }));
    } else if (line.trim()) {
      // Regular paragraph
      children.push(new Paragraph({
        text: line,
        spacing: { after: 200 },
      }));
    }
  });
  
  const doc = new Document({
    sections: [{
      properties: {},
      children: children,
    }],
  });
  
  // Generate and save
  const blob = await Packer.toBlob(doc);
  const filename = `${queryData.company_name}_analysis_${queryData.query_id}.docx`;
  saveAs(blob, filename);
};