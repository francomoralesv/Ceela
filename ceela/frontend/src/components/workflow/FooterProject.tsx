import React from "react";
//Components
import ProjectStatus from "@/components/projects/ProjectStatus";

interface FooterProjectProps {
  projectId: number | null;
  projectStatus: string | null;
}

const FooterProject: React.FC<FooterProjectProps> = (props) => {
  return (
    <>
      {props.projectId && (
        <ProjectStatus
          status={props.projectStatus || ""}
          projectId={String(props.projectId)}
        />
      )}
    </>
  );
};

export default FooterProject;
