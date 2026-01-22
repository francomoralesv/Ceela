import React, { useState, useMemo } from "react";

const collator = new Intl.Collator("es", { sensitivity: "base" }); // ①
const isNumeric = (v: any) =>                                      // ②
  typeof v === "number" ||
  (!!v && !Array.isArray(v) && !isNaN(parseFloat(v as any)));

interface Column {
  headerName: string | React.ReactNode;
  field: string;
  headerStyle?: React.CSSProperties;
  renderCell?: (row: any) => React.ReactNode;
  headerClick?: () => void; // Optional property for header click handler
  sortable?: boolean;
}

interface TablesParametersProps {
  columns: Column[];
  data: any[];
  multiHeader?: MultiHeader;
}

interface HeaderCell {
  label: string | React.ReactNode;
  colSpan?: number;
  rowSpan?: number;
  style?: React.CSSProperties;
  field?: string;
  sortable?: boolean;
}

type HeaderRow = HeaderCell[];

interface MultiHeader {
  rows: HeaderRow[];
}

interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

export default function TablesParameters({
  columns,
  data,
  multiHeader,
}: TablesParametersProps) {
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(null);


  const handleSort = (field: string) => {
    setSortConfig((current) => {
      if (current?.field === field) {
        return current.direction === 'asc'
          ? { field, direction: 'desc' }
          : null;
      }
      return { field, direction: 'asc' };
    });
  };


  const unwrap = (v: any): string | number | Date | null => {
    // Handle Date objects or date strings
    if (v instanceof Date) return v;
    if (typeof v === 'string' && !isNaN(Date.parse(v))) return new Date(v);
    
    // 1) Si es un elemento React
    if (React.isValidElement(v)) {
      const children = (v as React.ReactElement<any>).props.children;
      if (typeof children === "string") {
        // Check if children is a date string
        const date = new Date(children);
        if (!isNaN(date.getTime())) return date;
      }
      // 1a) Si los hijos son un string o number, simplemente lo devolvemos
      if (typeof children === "string" || typeof children === "number") {
        return children;
      }
      // 1b) Si es un array (p. ej. [ 'foo', <b>bar</b> ]), concatenamos todo
      if (Array.isArray(children)) {
        return children.map((c) => (typeof c === "string" ? c : "")).join("");
      }
    }
    // 2) Si no es un ReactNode, devolvemos el valor crudo (string, number, null…)
    return v;
  };

  const sortedData = useMemo(() => {
    if (!sortConfig) return data;

    const { field, direction } = sortConfig;
    const dir = direction === "asc" ? 1 : -1;

    return [...data].sort((a, b) => {
      const rawA = a[field];
      const rawB = b[field];
      const aVal = unwrap(rawA);
      const bVal = unwrap(rawB);

      // Null / undefined al final, independientemente de asc/desc
      if (aVal == null) return 1;
      if (bVal == null) return -1;

      // Handle dates
      if (aVal instanceof Date && bVal instanceof Date) {
        return (aVal.getTime() - bVal.getTime()) * dir;
      }

      // ④ Orden numérico robusto
      if (isNumeric(aVal) && isNumeric(bVal)) {
        return (parseFloat(String(aVal)) - parseFloat(String(bVal))) * dir;
      }

      // ⑤ Orden alfabético «humano» para español
      return collator.compare(String(aVal), String(bVal)) * dir;
    });
  }, [data, sortConfig]);


  return (
    <div className="container-fluid p-0">
      <div className="row g-0">
        <div className="col-12 p-0 d-flex flex-column">
          <div
            className="table-responsive w-100"
            style={{
              maxHeight: "400px", // Limitamos la altura para que tenga un scroll si es necesario
            }}
          >
            <table className="table table-hover table-sm mb-0">
            <thead>
  {multiHeader && multiHeader.rows.length > 0 ? (
    <>
      {multiHeader.rows.map((row, rowIndex) => {
        // ¿Estamos en la última fila de multiHeader?
        const isSortRow = rowIndex === multiHeader.rows.length - 1;

        return (
          <tr key={rowIndex}>
            {row.map((cell, cellIndex) => {
              // Solo sortable si estamos en la última fila y la celda tiene `field`
              const canSort = !!cell.field && (cell.sortable ?? true);
              const isActive = sortConfig?.field === cell.field;

              return (
                <th
                  key={cellIndex}
                  colSpan={cell.colSpan}
                  rowSpan={cell.rowSpan}
                  style={{
                    position: 'sticky',
                    top: 0,
                    background: 'white', // O el color de fondo de tu tabla
                    zIndex: 1,
                    cursor: canSort ? 'pointer' : undefined,
                    ...cell.style,
                  }}
                  className="text-center align-middle"
                  onClick={canSort ? () => handleSort(cell.field!) : undefined}
                >
                  {cell.label}
                  {isActive && sortConfig && (
                    <span className="ms-1">
                      {sortConfig.direction === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </th>
              );
            })}

            {/* opcional: si la suma de colSpan de la fila 0 es menor que columns.length, rellena vacíos */}
            {rowIndex === 0 &&
              row.reduce((sum, c) => sum + (c.colSpan ?? 1), 0) < columns.length && (
                <th
                  colSpan={
                    columns.length -
                    row.reduce((sum, c) => sum + (c.colSpan ?? 1), 0)
                  }
                  className="text-center align-middle"
                />
              )}
          </tr>
        );
      })}
    </>
  ) : (
    // Si no hay multiHeader, cae en la fila típica de columns
    <tr>
      {columns.map((col) => {
        const isActive = sortConfig?.field === col.field;
        return (
          <th
            key={col.field}
            className="text-center align-middle"
            onClick={() => col.sortable !== false && handleSort(col.field)}
            style={{
              position: 'sticky',
              top: 0,
              background: 'white', // O el color de fondo de tu tabla
              zIndex: 1,
              cursor: col.sortable !== false ? 'pointer' : 'default',
              ...col.headerStyle,
            }}
          >
            {col.headerName}
            {isActive && <span className="ms-1">{sortConfig!.direction === 'asc' ? '↑' : '↓'}</span>}
          </th>
        );
      })}
    </tr>
  )}
</thead>




              <tbody>
                {sortedData?.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {columns?.map((col) => (
                      <td
                        key={col.field}
                        className="text-center align-middle"
                        style={{
                          padding: "8px 2px",
                          minWidth: "100px",
                          cursor: "pointer",
                          transition: "background-color 0.2s",
                        }}
                      >
                        {col.renderCell ? col.renderCell(row) : row[col.field]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
