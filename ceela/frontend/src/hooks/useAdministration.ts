import { useState, useCallback } from 'react';
import axios from 'axios';
import Swal from 'sweetalert2';
import { Material, Detail, Element } from '../types/administration';
import { constantUrlApiEndpoint } from '../utils/constant-url-endpoint';

export const useAdministration = () => {
  const [materialsList, setMaterialsList] = useState<Material[]>([]);
  const [details, setDetails] = useState<Detail[]>([]);
  const [elementsList, setElementsList] = useState<Element[]>([]);

  const handleLogout = useCallback(() => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  }, []);

  const fetchMaterialsList = useCallback(async (page: number): Promise<void> => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        Swal.fire("Token no encontrado", "Inicia sesión.", "warning");
        handleLogout();
        return;
      }
      const url = `${constantUrlApiEndpoint}/admin/constants/?page=${page}&per_page=500`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      console.log("[fetchMaterialsList] Materiales recibidos:", response.data);
      const mappedMaterials = (response.data.constants || []).map(
        (mat: Material & { id_material?: number }) => ({
          ...mat,
          material_id: mat.id_material || mat.id,
        })
      );
      setMaterialsList(mappedMaterials);
    } catch (error) {
      console.error("[fetchMaterialsList] Error al obtener lista de materiales:", error);
      Swal.fire("Error", "Error al obtener materiales. Ver consola.", "error").then(() => {
        handleLogout();
      });
    }
  }, [handleLogout]);

  const fetchDetails = useCallback(async (): Promise<void> => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        Swal.fire("Token no encontrado", "Inicia sesión.", "warning");
        handleLogout();
        return;
      }
      
      // Cambiar esta URL para que coincida con la estructura usada en DetallesConstructivosTab
      const url = `${constantUrlApiEndpoint}/details/`;
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.get(url, { headers });
      console.log("[fetchDetails] Detalles recibidos:", response.data);
      const mappedDetails = (response.data || []).map(
        (det: Detail & { id_material?: number }) => ({
          ...det,
          material_id: det.id_material || det.material_id,
        })
      );
      console.log("[fetchDetails] Detalles mapeados:", mappedDetails);
      setDetails(mappedDetails);
    } catch (error) {
      console.error("[fetchDetails] Error al obtener detalles:", error);
      Swal.fire("Error", "Error al obtener detalles. Ver consola.", "error").then(() => {
        handleLogout();
      });
    }
  }, [handleLogout]);

  const fetchElements = useCallback(async (): Promise<void> => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        Swal.fire("Token no encontrado", "Inicia sesión.", "warning");
        handleLogout();
        return;
      }
      const url = `${constantUrlApiEndpoint}/admin/elements/`;
      const headers = { Authorization: `Bearer ${token}`, Accept: "application/json" };
      const response = await axios.get(url, { headers });
      console.log("[fetchElements] Elementos recibidos:", response.data);
      setElementsList(response.data || []);
    } catch (error) {
      console.error("[fetchElements] Error al obtener elementos:", error);
      Swal.fire("Error", "Error al obtener elementos. Ver consola.", "error").then(() => {
        handleLogout();
      });
    }
  }, [handleLogout]);

  return {
    materialsList,
    details,
    elementsList,
    fetchMaterialsList,
    fetchDetails,
    fetchElements,
    handleLogout
  };
};