import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { Document, Packer, Paragraph, TextRun, HeadingLevel } from 'docx';
import { saveAs } from 'file-saver';

/**
 * Export analysis to PDF with proper formatting and spacing
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
  const checkPageBreak = (requiredSpace = 10) => {
    if (yPosition + requiredSpace > pageHeight - margin) {
      doc.addPage();
      yPosition = margin;
      return true;
    }
    return false;
  };
  
  // Title
  doc.setFontSize(20);
  doc.setFont(undefined, 'bold');
  doc.text('Competitive Intelligence Report', margin, yPosition);
  yPosition += 12;
  
  // Metadata section
  doc.setFontSize(10);
  doc.setFont(undefined, 'normal');
  
  doc.text(`Company: ${queryData.company_name}`, margin, yPosition);
  yPosition += 6;
  
  const queryLines = doc.splitTextToSize(`Query: ${queryData.query}`, maxLineWidth);
  doc.text(queryLines, margin, yPosition);
  yPosition += (queryLines.length * 6) + 2;
  
  doc.text(`Competitors: ${queryData.competitors.join(', ')}`, margin, yPosition);
  yPosition += 6;
  
  doc.text(`Generated: ${new Date(queryData.created_at).toLocaleString()}`, margin, yPosition);
  yPosition += 6;
  
  doc.text(`Status: ${queryData.status}`, margin, yPosition);
  yPosition += 10;
  
  // Add separator line
  doc.setDrawColor(200, 200, 200);
  doc.line(margin, yPosition, pageWidth - margin, yPosition);
  yPosition += 10;
  
  // Analysis content
  if (queryData.analysis) {
    const lines = queryData.analysis.split('\n');
    
    for (let line of lines) {
      if (line.trim() === '') {
        yPosition += 3;
        continue;
      }
      
      // Explicitly handle Risk / Recommendation headings without bold
      if (line.startsWith('## Risk') || line.startsWith('## Recommendation')) {
        checkPageBreak(15);
        yPosition += 5;
        doc.setFontSize(14);
        doc.setFont(undefined, 'normal'); // ensure normal weight
        const headerText = line.replace('## ', '');
        doc.text(headerText, margin, yPosition);
        yPosition += 8;
        continue;
      }

      // Handle ## Headers (other main sections)
      if (line.startsWith('## ')) {
        checkPageBreak(15);
        yPosition += 5;
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        const headerText = line.replace('## ', '').replace(/\*/g, '');
        doc.text(headerText, margin, yPosition);
        yPosition += 8;
        doc.setFontSize(10);
        doc.setFont(undefined, 'normal');
        continue;
      }
      
      // Handle ### Sub-headers
      if (line.startsWith('### ')) {
        checkPageBreak(12);
        yPosition += 4;
        doc.setFontSize(12);
        doc.setFont(undefined, 'bold');
        const subHeaderText = line.replace('### ', '').replace(/\*/g, '');
        doc.text(subHeaderText, margin, yPosition);
        yPosition += 7;
        doc.setFontSize(10);
        doc.setFont(undefined, 'normal');
        continue;
      }
      
      // Handle bold lines only if explicitly marked
      if (line.trim().startsWith('**') && line.trim().endsWith('**')) {
        checkPageBreak(8);
        doc.setFont(undefined, 'bold');
        const boldText = line.replace(/\*\*/g, '').trim();
        const wrappedLines = doc.splitTextToSize(boldText, maxLineWidth);
        doc.text(wrappedLines, margin, yPosition);
        yPosition += (wrappedLines.length * 5.5) + 2;
        doc.setFont(undefined, 'normal');
        continue;
      }
      
      // Bullet points
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        checkPageBreak(8);
        const bulletText = line.trim().substring(2).replace(/\*\*/g, '');
        const wrappedLines = doc.splitTextToSize(`• ${bulletText}`, maxLineWidth - 5);
        doc.text(wrappedLines, margin + 5, yPosition);
        yPosition += (wrappedLines.length * 5.5) + 1;
        continue;
      }
      
      // Numbered lists
      if (line.trim().match(/^\d+\. /)) {
        checkPageBreak(8);
        const listText = line.trim().replace(/\*\*/g, '');
        const wrappedLines = doc.splitTextToSize(listText, maxLineWidth - 5);
        doc.text(wrappedLines, margin + 5, yPosition);
        yPosition += (wrappedLines.length * 5.5) + 1;
        continue;
      }
      
      // Regular paragraph
      checkPageBreak(8);
      const cleanLine = line.replace(/\*\*/g, '').trim();
      if (cleanLine) {
        const wrappedLines = doc.splitTextToSize(cleanLine, maxLineWidth);
        doc.text(wrappedLines, margin, yPosition);
        yPosition += (wrappedLines.length * 5.5) + 1;
      }
    }
  }
  
  // Save PDF
  const filename = `${queryData.company_name}_analysis_${queryData.query_id}.pdf`;
  doc.save(filename);
};

/**
 * Export analysis to Word (.docx)
 */
export const exportToWord = async (queryData) => {
  const sections = queryData.analysis.split('\n').filter(line => line.trim());
  
  const children = [
    new Paragraph({
      text: 'Competitive Intelligence Report',
      heading: HeadingLevel.HEADING_1,
      spacing: { after: 400 },
    }),
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
    new Paragraph({
      text: 'Analysis',
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 400, after: 200 },
    }),
  ];
  
  sections.forEach((line) => {
    const cleanLine = line.replace(/\*\*/g, '');
    
    if (line.startsWith('# ')) {
      children.push(new Paragraph({
        text: cleanLine.substring(2),
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 400, after: 200 },
      }));
    } else if (line.startsWith('## ')) {
      // Special handling: Risk / Recommendation not bold
      if (line.startsWith('## Risk') || line.startsWith('## Recommendation')) {
        children.push(new Paragraph({
          text: cleanLine.substring(3),
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 300, after: 150 },
        }));
      } else {
        children.push(new Paragraph({
          text: cleanLine.substring(3),
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 300, after: 150 },
        }));
      }
    } else if (line.startsWith('### ')) {
      children.push(new Paragraph({
        text: cleanLine.substring(4),
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 200, after: 100 },
      }));
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      children.push(new Paragraph({
        text: cleanLine.substring(2),
        bullet: { level: 0 },
        spacing: { after: 100 },
      }));
    } else if (line.trim()) {
      children.push(new Paragraph({
        text: cleanLine,
        spacing: { after: 200 },
      }));
    }
  });
  
  const doc = new Document({ sections: [{ properties: {}, children }] });
  
  const blob = await Packer.toBlob(doc);
  const filename = `${queryData.company_name}_analysis_${queryData.query_id}.docx`;
  saveAs(blob, filename);
};
