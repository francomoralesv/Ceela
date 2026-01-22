import { useEffect, useCallback } from "react";
import axios from "axios";
import { notify } from "@/utils/notify";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import useToken from "./useToken";

interface UseFetchProjectStatusProps {
  projectId: number | null;
}

const useFetchProjectStatus = ({ projectId }: UseFetchProjectStatusProps) => {
  const { getToken } = useToken(); // Use the custom hook
  const fetchProjectStatus = useCallback(async () => {
    try {
      const token = getToken();
      if (!token || !projectId) return;
      const { data: projectData } = await axios.get(
        `${constantUrlApiEndpoint}/projects/${projectId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // console.log(projectData);
      return projectData?.status || "En proceso";
    } catch (error) {
      console.error("Error al obtener el estado del proyecto:", error);
      notify("Error al obtener el estado del proyecto.");
    }
  }, [projectId]);

  useEffect(() => {
    if (projectId) {
      fetchProjectStatus();
    }
  }, [projectId, fetchProjectStatus]);

  return { fetchProjectStatus };
};

export default useFetchProjectStatus;
