import { notify } from "@/utils/notify";

const useToken = () => {
  const getToken = (): string | null => {
    const token = localStorage.getItem("token");
    if (!token) {
      notify("Token no encontrado", "Inicia sesión.");
      return null;
    }
    return token;
  };

  return { getToken };
};

export default useToken;
