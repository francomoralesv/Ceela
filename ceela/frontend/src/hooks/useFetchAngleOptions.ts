import { getOrientationMapping2 } from "@/utils/azimut";
import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import { useEffect, useState } from "react";


interface AzimutOption {
  orientation: string;
  fullName: string;
  azimut: string;
}

const useFetchAngleOptions = () => {
  const [angleOptions, setAngleOptions] = useState<AzimutOption[]>([]);

  useEffect(() => {
    const fetchAngleOptions = async () => {
      try {
        const token = localStorage.getItem("token");
        const headers: HeadersInit = { "Content-Type": "application/json" };
        if (token) headers.Authorization = `Bearer ${token}`;
        const response = await fetch(`${constantUrlApiEndpoint}/angle-azimut`, {
          headers,
        });
        if (!response.ok) throw new Error("Error al obtener opciones de ángulo azimut");
        const options = await response.json();
        if (options){
          const formattedOptions=getOrientationMapping2(options) as unknown as AzimutOption[];
        setAngleOptions(formattedOptions);}
      } catch (error) {
        console.error(error);
      }
    };
    fetchAngleOptions();
  }, []);

  return [angleOptions, setAngleOptions] as const;
};

export default useFetchAngleOptions;