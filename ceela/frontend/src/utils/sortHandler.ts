import React, { useState } from "react";

interface SortHandlerProps<T> {
  data: T[];
  onSort: (sortedData: T[]) => void;
}

const SortHandler = <T extends Record<string, any>>({
  data,
  onSort,
}: SortHandlerProps<T>) => {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: "asc" | "desc";
  } | null>(null);

  const getNestedValue = (obj: any, key: string): any => {
    return key.split(".").reduce((acc, part) => acc && acc[part], obj);
  };

  const handleSort = (key: string) => {
    let direction: "asc" | "desc" = "asc";
    if (
      sortConfig &&
      sortConfig.key === key &&
      sortConfig.direction === "asc"
    ) {
      direction = "desc";
    }
    setSortConfig({ key, direction });

    const sortedData = [...data].sort((a, b) => {
      const aValue = getNestedValue(a, key)?.toString().toLowerCase() || "";
      const bValue = getNestedValue(b, key)?.toString().toLowerCase() || "";

      if (aValue < bValue) return direction === "asc" ? -1 : 1;
      if (aValue > bValue) return direction === "asc" ? 1 : -1;
      return 0;
    });

    onSort(sortedData);
    console.log(sortedData);
  };

  return { handleSort };
};

export default SortHandler;
