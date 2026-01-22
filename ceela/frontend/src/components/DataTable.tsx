import { ChevronLeft, ChevronRight, Inbox, Loader2 } from "lucide-react";
import React, { useState } from "react";
import Card from "./common/Card";
import IconButton from "./common/IconButton";
import SearchInput from "./inputs/SearchInput";

// ------- helpers de ordenamiento -------
const collator = new Intl.Collator("es", { sensitivity: "base" });

const isNumeric = (v: any) =>
  typeof v === "number" ||
  (!!v && !Array.isArray(v) && !isNaN(parseFloat(v as any)));

interface SortConfig {
  field: string | number;
  direction: "asc" | "desc";
}

interface DataTableProps<T> {
  data: T[];
  columns: {
    id: number | string;
    label: string;
    minWidth?: number;
    format?: any;
    cell?: (props: { row: T }) => React.ReactNode;
    sortable?: boolean;
  }[];
  loading?: boolean;
  onSearch?: (searchTerm: string) => void;
  pageSize?: number;
  enableSorting?: boolean;
  enableFiltering?: boolean;
  enableColumnVisibility?: boolean;
  createText?: string;
  createUrl?: string;
  showButton?: boolean;
}

const TablePagination: React.FC<{
  page: number;
  rowsPerPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onRowsPerPageChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
}> = ({ page, rowsPerPage, totalPages, onPageChange, onRowsPerPageChange }) => {
  const getPageNumbers = () => {
    const range = [];
    const maxVisiblePages = 5;

    if (totalPages <= maxVisiblePages + 2) {
      for (let i = 0; i < totalPages; i++) {
        range.push(i);
      }
      return range;
    }

    range.push(0);

    let start = Math.max(page - Math.floor(maxVisiblePages / 2), 1);
    const end = Math.min(start + maxVisiblePages - 1, totalPages - 2);

    if (end === totalPages - 2) {
      start = Math.max(end - maxVisiblePages + 1, 1);
    }

    if (start > 1) {
      range.push('...');
    }

    for (let i = start; i <= end; i++) {
      range.push(i);
    }

    if (end < totalPages - 2) {
      range.push('...');
    }

    range.push(totalPages - 1);

    return range;
  };

  return (
    <div className="d-flex flex-column flex-sm-row justify-content-between align-items-center gap-2 mt-1">
      <div
        className="w-100 w-sm-auto mb-2 mb-sm-0 mx-auto mx-sm-0"
        style={{ maxWidth: "180px" }}
      >
        <select
          className="form-select form-select-sm"
          value={rowsPerPage}
          onChange={onRowsPerPageChange}
        >
          <option value={5}>5 por página</option>
          <option value={10}>10 por página</option>
          <option value={25}>25 por página</option>
          <option value={50}>50 por página</option>
        </select>
      </div>
      <div className="d-flex align-items-center justify-content-center gap-1 gap-sm-2 w-100 w-sm-auto">
        <IconButton
          onClick={() => onPageChange(page - 1)}
          icon={ChevronLeft}
          disabled={page === 0}
        />
        <div className="d-flex align-items-center gap-1">
          {totalPages > 2 && getPageNumbers().map((pageNumber, index) => (
            pageNumber === '...' ? (
              <span key={`dots-${index}`} className="px-2">...</span>
            ) : (
              <button
                key={`page-${pageNumber}`}
                onClick={() => onPageChange(pageNumber as number)}
                className={`btn btn-sm ${page === pageNumber ? '' : ''}`}
                style={{
                  minWidth: '32px',
                  border: 'none',
                  backgroundColor: page === pageNumber ? 'var(--primary-color)' : 'transparent',
                  color: page === pageNumber ? '#fff' : 'var(--primary-color)'
                }}
              >
                {(pageNumber as number) + 1}
              </button>
            )
          ))}
        </div>
        <div className="flex-shrink-0 primary-db">
          <IconButton
            onClick={() => onPageChange(page + 1)}
            icon={ChevronRight}
            disabled={page >= totalPages - 1}
          />
        </div>
      </div>
    </div>
  );
}

export default function DataTable<T extends { [key: string]: any }>({
  data,
  columns,
  loading = false,
  pageSize = 10,
  createText,
  createUrl,
}: DataTableProps<T>) {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(pageSize);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(null);

  const handleSort = (field: string | number) => {
    setSortConfig((current) => {
      if (current?.field === field) {
        return current.direction === "asc"
          ? { field, direction: "desc" }
          : null;
      }
      return { field, direction: "asc" };
    });
  };

  const handleChangePage = (newPage: number) => {
    if (
      newPage >= 0 &&
      newPage < Math.ceil(filteredData.length / rowsPerPage)
    ) {
      setPage(newPage);
    }
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    setRowsPerPage(+event.target.value);
    setPage(0);
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
    setPage(0);
  };

  const filteredData = searchQuery.trim()
    ? data.filter((row) => {
      const combined = Object.values(row)
        .map((val) => {
          if (val === undefined || val === null) return "";
          if (typeof val === "object") return JSON.stringify(val);
          return String(val);
        })
        .join(" ")
        .toLowerCase();
      return combined.includes(searchQuery.toLowerCase());
    })
    : data;

  const getCurrentPageData = () => {
    const start = page * rowsPerPage;
    const end = start + rowsPerPage;
    return filteredData.slice(start, end);
  };

  const sortedData = React.useMemo(() => {
    const currentPageData = getCurrentPageData();
    
    if (!sortConfig) return currentPageData;
    
    const { field, direction } = sortConfig;
    const dir = direction === "asc" ? 1 : -1;

    return [...currentPageData].sort((a, b) => {
      const aVal = a[field];
      const bVal = b[field];

      if (aVal == null) return 1;
      if (bVal == null) return -1;

      if (isNumeric(aVal) && isNumeric(bVal)) {
        return (parseFloat(aVal) - parseFloat(bVal)) * dir;
      }
      return collator.compare(String(aVal), String(bVal)) * dir;
    });
  }, [filteredData, page, rowsPerPage, sortConfig]);

  const totalPages = Math.ceil(filteredData.length / rowsPerPage);

  return (
    <Card>
      <div className="row mb-3 mt-3">
        <div className="col-12">
          <div className="d-flex flex-column flex-sm-row gap-2">
            <SearchInput
              searchQuery={searchQuery}
              handleSearch={handleSearch}
              createUrl={createUrl}
              createText={createText}
              showButton={createText ? true : false}
            />
          </div>
        </div>
      </div>
      <div className="container-fluid p-0">
        <div className="row g-0">
          <div className="col-12 p-0">
            <div className="table-responsive w-100">
              <table className="table table-hover w-100 mb-0 ">
                <thead className="bg-light border-bottom">
                  <tr>
                    {columns.map((column) => (
                      <th
                        key={column.id.toString()}
                        style={{
                          color: "var(--primary-color)",
                          cursor: column.sortable === false ? "default" : "pointer",
                        }}
                        className="text-start"
                        onClick={() => column.sortable !== false && handleSort(column.id)}
                      >
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '4px',
                          whiteSpace: 'nowrap'
                        }}>
                          {column.label}
                          {sortConfig?.field === column.id && (
                            <span style={{ display: 'inline-flex' }}>
                              {sortConfig.direction === "asc" ? "↑" : "↓"}
                            </span>
                          )}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan={columns.length} className="text-center">
                        <Loader2
                          className="animate-spin me-2 inline"
                          size={18}
                        />
                        Cargando...
                      </td>
                    </tr>
                  ) : filteredData.length === 0 ? (
                    <tr>
                      <td colSpan={columns.length} className="text-center">
                        <Inbox className="me-2 inline" size={18} />
                        No hay datos disponibles
                      </td>
                    </tr>
                  ) : (
                    sortedData.map((row, index) => (
                      <tr key={index} className="align-middle">
                        {columns.map((column) => (
                          <td
                            key={column.id.toString()}
                            className="text-start p-2 p-md-3"
                          >
                            {column.cell
                              ? column.cell({ row })
                              : column.format
                                ? column.format(row[column.id], row)
                                : row[column.id]}
                          </td>
                        ))}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div></div></div>
      </div>
      <div className="row">
        <div className="col-md-12 mb-2">
          <TablePagination
            page={page}
            rowsPerPage={rowsPerPage}
            totalPages={totalPages}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </div>
      </div>
      <style jsx>{`
        .primary-db {
          background-color: var(--primary-color) !important;
        }
      `}</style>
    </Card>
  );
}
