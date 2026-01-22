import React from 'react';

interface Column {
    header: string;
    accessor: string;
    align?: 'left' | 'center' | 'right';
}

interface GenericTableProps<T> {
    columns: Column[];
    data: T[];
    searchTerm?: string;
    searchField?: keyof T;
    maxHeight?: string;
    isLoading?: boolean;
    emptyMessage?: string;
}

export function GenericTable<T extends Record<string, any>>({
    columns,
    data,
    searchTerm = '',
    searchField,
    maxHeight = '70vh',
    isLoading = false,
    emptyMessage = 'No hay datos para mostrar'
}: GenericTableProps<T>) {
    // Filter data based on search term if provided
    const filteredData = searchTerm && searchField
        ? data.filter(item => 
                String(item[searchField])
                    .toLowerCase()
                    .includes(searchTerm.toLowerCase())
            )
        : data;

    return (
        <div className="table-responsive">
            <div className="border rounded overflow-hidden">
                <div style={{ maxHeight, overflowY: "auto" }}>
                    <table className="table table-hover mb-0">
                        <thead>
                            <tr>
                                {columns.map((column, index) => (
                                    <th 
                                        key={index} 
                                        style={{ textAlign: column.align || "center" }}
                                    >
                                        {column.header}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {isLoading ? (
                                <tr>
                                    <td colSpan={columns.length} className="text-center">
                                        Cargando...
                                    </td>
                                </tr>
                            ) : filteredData.length > 0 ? (
                                filteredData.map((item, idx) => (
                                    <tr key={idx}>
                                        {columns.map((column, colIdx) => (
                                            <td 
                                                key={colIdx} 
                                                style={{ textAlign: column.align || "center" }}
                                            >
                                                {item[column.accessor]}
                                            </td>
                                        ))}
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={columns.length} className="text-center">
                                        {emptyMessage}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default GenericTable;