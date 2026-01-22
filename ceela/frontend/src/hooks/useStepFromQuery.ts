import { useEffect } from "react";
import { useRouter } from "next/router";

const useStepFromQuery = (setStep: (step: number) => void) => {
  const router = useRouter();

  useEffect(() => {
    if (router.query.step) {
      const queryStep = parseInt(router.query.step as string, 10);
      if (!isNaN(queryStep)) {
        setStep(queryStep);
      }
    }
  }, [router.query.step, setStep]);
};

export default useStepFromQuery;
