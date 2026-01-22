/**
 * Formats a value for display in tables and forms
 * @param value The value to format
 * @param isNumericField If true, formats number with 2 decimal places
 * @returns Formatted value as string
 */
export const displayValue = (value: any, isNumericField: boolean = false): string => {
    if (value === 0 || value === "N/A") return "-";
    if (isNumericField && typeof value === 'number') {
        return value.toFixed(2);
    }
    return String(value);
};
