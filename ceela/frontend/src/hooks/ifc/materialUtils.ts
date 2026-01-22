import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";

export const materialsCache: Record<string, any> = {};

/**
 * Gets material information by code, using cache to avoid redundant API calls
 * @param code The material code to look up
 * @returns Material information or null if not found
 */
export const getMaterialByCode = async (code: string) => {
    if (materialsCache[code]) {
        console.log(`Using cached material for code: ${code}`);
        return materialsCache[code];
    }

    try {
        const token = localStorage.getItem("token");
        console.log(`Fetching material for code: ${code}`);
        const response = await fetch(`${constantUrlApiEndpoint}/constants-code_ifc?code_ifc=${code}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
        });
        if (!response.ok) {
            throw new Error("Failed to fetch material info");
        }
        const data = await response.json();
        materialsCache[code] = data;
        return data;
    } catch (error) {
        console.error("Error fetching material info:", error);
        return null;
    }
};
