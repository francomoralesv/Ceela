import { useEffect, useState } from "react";
import useProjectId from "@/hooks/useProjectId";
import useFetchProjectStatus from "./useFetchProjectStatus";

const useProjectInitialization = () => {
  const { projectId, setProjectId } = useProjectId(); // Use the useProjectId hook
  const [projectName, setProjectName] = useState<string>("Nombre no definido");
  const [projectDepartment, setProjectDepartment] =
    useState<string>("Región no definida");
  const [projectStatus, setProjectStatus] = useState("En proceso");
  const [hasLoaded, setHasLoaded] = useState<boolean>(false);

  const { fetchProjectStatus } = useFetchProjectStatus({ projectId });

  useEffect(() => {
    const storedProjectName =
      localStorage.getItem("project_name") || "Nombre no definido";
    const storedProjectDepartment =
      localStorage.getItem("project_department") || "Región no definida";
    setProjectName(storedProjectName);
    setProjectDepartment(storedProjectDepartment);

    fetchProjectStatus().then((status: string) => {
      setProjectStatus(status);
    });

    setHasLoaded(true);
  }, [fetchProjectStatus]);

  return {
    projectId,
    projectName,
    projectDepartment,
    hasLoaded,
    projectStatus,
    setProjectId,
  };
};

export default useProjectInitialization;
