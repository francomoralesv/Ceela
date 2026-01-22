import * as XLSX from 'xlsx';

export function exportToExcel({
  data,
  fileName = 'reporte.xlsx',
  sheetName = 'Sheet1',
  headers = [],
  title = ''
}: {
  data: any[],
  fileName?: string,
  sheetName?: string,
  headers?: string[],
  title?: string
}) {
  const wsData = [];

  // Add title if provided
  if (title) {
    wsData.push([title]);
  }

  // Add generation date
  const generationDate = new Date().toLocaleString('es-CL');
  wsData.push([`Fecha de Generación: ${generationDate}`]);

  // Add an empty row for spacing
  wsData.push([]);

  // Add headers
  if (headers.length > 0) {
    wsData.push(headers);
  }

  // Add data rows
  wsData.push(...data);

  const ws = XLSX.utils.aoa_to_sheet(wsData);

  // Merge cells for title and date
  const merges = [];
  const headerCount = headers.length > 0 ? headers.length : 1;

  if (title) {
    merges.push({ s: { r: 0, c: 0 }, e: { r: 0, c: headerCount - 1 } }); // Merge title row
  }
  merges.push({ s: { r: 1, c: 0 }, e: { r: 1, c: headerCount - 1 } }); // Merge date row

  ws['!merges'] = merges;

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, sheetName);
  XLSX.writeFile(wb, fileName);
}
