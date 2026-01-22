import axios from "axios";
import { notify } from "@/utils/notify";
import { constantUrlApiEndpoint } from "../utils/constant-url-endpoint";


export const useCrudOperations = () => {
  const handleCreate = async (
    payload: any,
    endpoint: string,
    successMessage: string,
    fetchData: () => Promise<void>
  ) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        notify("Token no encontrado. Inicia sesión.");
        return;
      }

      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };

      const url = `${constantUrlApiEndpoint}/${endpoint}`;
      const response = await axios.post(url, payload, { headers });

      if (response.status === 200) {
        notify(successMessage);
        await fetchData();
        return true;
      }
    } catch (error) {
      console.error(`[handleCreate] Error:`, error);
      notify("No se pudo crear el elemento");
    }
    return false;
  };

  const handleEdit = async (
    id: number,
    payload: any,
    endpoint: string,
    successMessage: string,
    fetchData: () => Promise<void>
  ) => {
      const token = localStorage.getItem("token");
      if (!token) {
        notify("Token no encontrado. Inicia sesión.");
        return;
      }

      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };

      const url = `${constantUrlApiEndpoint}/${endpoint}/${id}/update`;
      const response = await axios.put(url, payload, { headers });

      if (response.status === 200) {
        notify(successMessage);
        await fetchData();
      }
    
  };

  const handleDelete = async (
    id: number,
    endpoint: string,
    successMessage: string,
    fetchData: () => Promise<void>
  ) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        notify("Token no encontrado. Inicia sesión.");
        return;
      }

      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };

      const url = `${constantUrlApiEndpoint}/${endpoint}/${id}/delete`;
      const response = await axios.delete(url, { headers });

      if (response.status === 200) {
        notify(successMessage);
        await fetchData();
      }
    } catch (error) {
      console.error(`[handleDelete] Error:`, error);
      notify("No se pudo eliminar el elemento");
    }
  };

  return { handleCreate, handleEdit, handleDelete };
};