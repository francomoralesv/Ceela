import { useEffect } from "react";
import { useRouter } from "next/router";
import { notify } from "@/utils/notify";

const useRedirectIfNoProject = (
  hasLoaded: boolean,
  projectId: number | null
) => {
  const router = useRouter();

  useEffect(() => {
    if (hasLoaded && projectId === null) {
      notify(
        "Ningún proyecto está seleccionado",
        "Serás redirigido a la creación de proyecto"
      );
      router.push("/workflow-part1-create");
    }
  }, [hasLoaded, projectId, router]);
};

export default useRedirectIfNoProject;
