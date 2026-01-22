import React, { useMemo, useState } from "react";
import SearchParameters from "@/components/inputs/SearchParameters";

/**
 * Generic search wrapper that encapsulates all the “buscar” logic that was
 * scattered through Detalles constructivos (muros, techumbre y pisos).
 *
 * @template T – row shape of each table
 */
export interface SearchFilterProps<T> {
  /** Raw list that comes from the API */
  data: T[];
  /** Keys inside each row where the query should be matched (string‑based) */
  searchKeys: (keyof T | string)[];
  /** Placeholder text for the input */
  placeholder?: string;
  /** Render‑prop that receives the filtered data */
  children: (
    /** Filtered list */ filtered: T[],
    /** Current query */ query: string,
    /** Setter so a parent can change it programmatically */ setQuery: (q: string) => void
  ) => React.ReactNode;
  /** Optional "+ Nuevo" button shown at the right edge */
  showNewButton?: boolean;
  /** Callback when the "+ Nuevo" button is clicked */
  onNew?: () => void;
}

/**
 * **SearchFilter** keeps the query state, performs the filtering and then hands
 * both the filtered data **and** the controls back to you through a render‑prop.
 *
 * ```tsx
 * <SearchFilter data={muros} searchKeys={["name_detail"]}>
 *   {(filtered) => <TablesParameters data={buildRows(filtered)} />}
 * </SearchFilter>
 * ```
 */
export default function SearchFilter<T extends Record<string, unknown>>({
  data,
  searchKeys,
  placeholder = "Buscar…",
  children,
  showNewButton = false,
  onNew,
}: SearchFilterProps<T>) {
  const [query, setQuery] = useState("");

  /** Normalised query */
  const queryLower = query.trim().toLowerCase();

  /**
   * Memoised, **case‑insensitive** filter that only recalculates when `data` or
   * `query` change.
   */
  const filtered = useMemo(() => {
    if (!queryLower) return data;
    return data.filter((row) =>
      searchKeys.some((k) => {
        const value = String((row as any)[k] ?? "").toLowerCase();
        return value.includes(queryLower);
      })
    );
  }, [data, searchKeys, queryLower]);

  return (
    <>
      <SearchParameters
        value={query}
        onChange={setQuery}
        placeholder={placeholder}
        showNewButton={showNewButton}
        onNew={onNew ?? (() => {})}
        /* allow parent styling overrides */
        style={{ marginBottom: "1rem" }}
      />
      {children(filtered, query, setQuery)}
    </>
  );
}

/* -------------------------------------------------------------------------- */
/*                       🛠  HOW TO USE IT IN YOUR PAGE                       */
/* -------------------------------------------------------------------------- */
// 1️⃣  Import it where you render each table                                   
// import SearchFilter from "@/components/constructive_details/SearchFilter";
//
// 2️⃣  Replace the old <SearchParameters> + manual .filter() with:
//
// <SearchFilter
//   data={murosTabList}
//   searchKeys={["name_detail"]}
//   placeholder="Buscar muros"
//   showNewButton   // idem a tu antiguo ‘SearchParameters’
//   onNew={handleNewButtonClick}
// >
//   {(filteredMuros) => {
//       const murosData = buildMurosRows(filteredMuros);
//       return <TablesParameters columns={columnsMuros} data={murosData} />;
//   }}
// </SearchFilter>
//
// Re‑use the same pattern for Techumbre y Pisos cambiando `data`, `searchKeys`
// y `placeholder`. 🚀
/* -------------------------------------------------------------------------- */
