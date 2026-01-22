import axios, { AxiosRequestConfig } from "axios";
import { useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_ENDPOINT || "https://localhost:8000";

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const request = async <T>(method: "get" | "post" | "put" | "delete" | "patch", endpoint: string, data?: any, config?: AxiosRequestConfig) => {
    setLoading(true);
    setError(null);

    const token = localStorage.getItem("token");
    const headers = {
      ...config?.headers,
      Authorization: token ? `Bearer ${token}` : "",
    };

    const reformattedEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
    const fullUrl=`${API_BASE_URL}/${reformattedEndpoint}`
    try {
      const response = await axios({
        method,
        url: fullUrl,
        data,
        ...config,
        headers,
      });
      return response.data as T;
    } catch (err) {
      console.log( "Err ", err);
      if (axios.isAxiosError(err) && err.response?.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
        return;
      }
      setError("Error en la petición");
      console.error(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    get: (endpoint: string, config?: AxiosRequestConfig) => request<any>("get", endpoint, null, config),
    post: (endpoint: string, data: any, config?: AxiosRequestConfig) => request<any>("post", endpoint, data, config),
    put: (endpoint: string, data: any, config?: AxiosRequestConfig) => request<any>("put", endpoint, data, config),
    patch:(endpoint: string, data: any, config?: AxiosRequestConfig) => request<any>("patch", endpoint, data, config),
    del:(endpoint: string, config?: AxiosRequestConfig) => request<any>("delete", endpoint, null, config),
    loading,
    error,
  };
}
