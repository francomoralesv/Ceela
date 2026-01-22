import axios from "axios";

export const getRuntimeConfig = async (): Promise<{ apiEndpoint: string }> => {
  try {
    if (typeof window !== "undefined") {
      const { data } = await axios.get("/api/config");
      return { apiEndpoint: data.apiEndpoint };
    }
    return { apiEndpoint: process.env.NEXT_PUBLIC_API_ENDPOINT || "https://localhost:8000" };
  } catch (error) {
    console.error("Error fetching API config:", error);
    return { apiEndpoint:  "https://localhost:8000" }; 
  }
};
