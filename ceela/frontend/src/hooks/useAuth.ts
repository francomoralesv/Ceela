// hooks/useAuth.ts
import { useRouter } from "next/router";
import { useEffect } from "react";
import { jwtDecode } from "jwt-decode";

interface JwtPayload {
  exp: number;
  // otras propiedades si las necesitas
}

const useAuth = () => {
  const router = useRouter();

  useEffect(() => {
    console.log("[useAuth] Iniciando verificación de autenticación...");
    const token = localStorage.getItem("token");

    if (!token) {
      console.warn("[useAuth] No se encontró token. Redirigiendo a /login.");
      router.push("/login");
      return;
    }

    try {
      const decoded = jwtDecode<JwtPayload>(token);
      const expirationTime = decoded.exp * 1000; // convertir a milisegundos
      console.log("[useAuth] Token encontrado, expira en:", new Date(expirationTime));

      if (Date.now() >= expirationTime) {
        console.warn("[useAuth] Token expirado. Eliminando token y redirigiendo a /login.");
        localStorage.removeItem("token");
        router.push("/login");
      } else {
        console.log("[useAuth] Token válido.");
      }
    } catch (error) {
      console.error("[useAuth] Error al decodificar el token. Redirigiendo a /login.", error);
      localStorage.removeItem("token");
      router.push("/login");
    }
  }, [router]);
};

export default useAuth;
