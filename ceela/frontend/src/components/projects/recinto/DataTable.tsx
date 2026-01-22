import React from 'react';

export interface TableProps {
    title?: string;
    headers: React.ReactNode[];
    rows: React.ReactNode[][];
    className?: string;
}

/**
 * Reusable table component for displaying data
 */
const DataTable: React.FC<TableProps> = ({ title, headers, rows, className = '' }) => {
    return (
        <div className="table-responsive">
            {title && <h4 className="mb-3">{title}</h4>}
            <table className={`table table-bordered ${className}`}>
                <thead>
                    <tr>
                        {headers.map((header, idx) => (
                            <th key={idx} className="text-center">
                                {header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, rowIdx) => (
                        <tr key={rowIdx}>
                            {row.map((cell, cellIdx) => (
                                <td key={cellIdx}>{cell}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default DataTable;
