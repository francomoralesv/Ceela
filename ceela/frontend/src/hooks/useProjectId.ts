import { useState, useEffect } from "react";

const useProjectId = () => {
  const [projectId, setProjectId] = useState<number | null>(null);

  useEffect(() => {
    const storedProjectId = localStorage.getItem("project_id");
    if (storedProjectId) {
      setProjectId(Number(storedProjectId));
    }
  }, []);

  const updateProjectId = (id: number | null) => {
    if (id) {
      localStorage.setItem("project_id", id.toString());
    } else {
      localStorage.removeItem("project_id");
    }
    setProjectId(id);
  };

  return { projectId, setProjectId: updateProjectId };
};

export default useProjectId;
