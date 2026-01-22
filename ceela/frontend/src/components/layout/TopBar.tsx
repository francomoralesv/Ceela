'use client'
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useRef, useState } from "react";
import { constantUrlApiEndpoint } from "../../utils/constant-url-endpoint";

interface TopBarProps {
  sidebarWidth: string;
}

// Función para convertir el valor del rol a texto (se retorna directamente si ya es "Administrador" u "Desarrollador")
const getUserTypeText = (role: string): string => {
  if (role === "Administrador" || role === "Desarrollador") return role;
  switch (role) {
    case "1":
      return "Administrador";
    case "2":
      return "Desarrollador";
    default:
      return "Desarrollador";
  }
};

const TopBar = ({}: TopBarProps) => {
  const [user, setUser] = useState({
    name: "Usuario",
    email: "",
    userType: "Tipo de Usuario",
  });
  const [menuOpen, setMenuOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const router = useRouter();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Función para cargar datos desde localStorage
  const loadProfile = () => {
    const storedProfile = localStorage.getItem("userProfile");
    if (storedProfile) {
      try {
        const parsedProfile = JSON.parse(storedProfile);
        const emailFromProfile = parsedProfile.email || localStorage.getItem("email") || "";
        const nameFromProfile = parsedProfile.name || localStorage.getItem("user_name") || "Usuario";
        const userTypeFromProfile = parsedProfile.userType || localStorage.getItem("role_id") || "Administrador";

        setUser({
          name: nameFromProfile,
          email: emailFromProfile,
          userType: userTypeFromProfile,
        });
      } catch (err) {
        console.error("Error al parsear el perfil desde localStorage:", err);
      }
    } else {
      setUser({
        name: localStorage.getItem("user_name") || "Usuario",
        email: localStorage.getItem("email") || "",
        userType: localStorage.getItem("role_id") || "Tipo de Usuario",
      });
    }
  };

  useEffect(() => {
    setIsMounted(true);
    loadProfile();
  }, []);

  // Escucha el evento "profileUpdated" para recargar el perfil
  useEffect(() => {
    const handleProfileUpdate = () => {
      loadProfile();
    };

    window.addEventListener("profileUpdated", handleProfileUpdate);
    return () => {
      window.removeEventListener("profileUpdated", handleProfileUpdate);
    };
  }, []);

  // Cerrar el menú si se hace clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownRef]);

  if (!isMounted) {
    return null;
  }

  const handleLogout = async () => {
      const token = localStorage.getItem("token"); // Obtener el token del usuario
      if (!token) {
          router.push("/login");
          return;
      }
  
      try {
          const response = await fetch(`${constantUrlApiEndpoint}/logout`, {
              method: "DELETE",
              headers: {
                  "Authorization": `Bearer ${token}`, // Token en el header para autenticar al usuario
                  "token": token, // Enviar el token a revocar (según la definición del endpoint)
                  "Content-Type": "application/json"
              }
          });
  
          if (response.ok) {
              console.log("Sesión cerrada correctamente");
          } else {
              console.error("Error al cerrar sesión", await response.json());
          }
      } catch (error) {
          console.error("Error de red:", error);
      }
  
      // Limpiar el almacenamiento local y redirigir al login
      localStorage.clear();
      router.push("/login");
  };

  return (
    <nav
      className="navbar shadow-sm px-4"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1100,
        minHeight: "120px",
        padding: "10px 20px",
        backgroundColor: "rgba(255, 255, 255, 0.2)",
        backdropFilter: "blur(7px)",
        boxShadow: "0px 12px 16px rgba(0, 0, 0, 0.3)",
        width: "100%",
        overflow: "visible",
      }}
    >
      <div
        className="container-fluid d-flex justify-content-center align-items-center"
        style={{ flexWrap: "wrap" }}
      >
        {/* Contenedor de la imagen centrada */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            flex: 1,
          }}
        >
          {/* Aquí puedes colocar tu logo si lo requieres */}
        </div>

        <div
          className="dropdown"
          style={{ position: "relative", fontFamily: "var(--font-family-base)" }}
          ref={dropdownRef}
        >
          {/* Botón del usuario */}
          <button
            className="btn d-flex align-items-center"
            onClick={() => setMenuOpen(!menuOpen)}
            style={{
              background: "transparent",
              border: "none",
              padding: 0,
              display: "flex",
              alignItems: "center",
              cursor: "pointer",
            }}
          >
            <Image
              src="/assets/images/user_icon.png"
              alt="User"
              width={50}
              height={50}
              className="rounded-circle"
              style={{ marginRight: "8px" }}
            />

            <div className="d-none d-md-flex flex-column align-items-start">
              <span style={{ color: "var(--primary-color)" }}>
                {user.email || "Email"}
              </span>
              <span style={{ display: "flex", alignItems: "center" }}>
                {user.name || "Usuario"}{" "}
                <i className="bi bi-caret-down-fill ms-1" style={{ fontSize: "14px" }} />
              </span>
              <span
                style={{
                  fontSize: "12px",
                  backgroundColor: "var(--primary-color)",
                  color: "white",
                  padding: "5px 10px",
                  borderRadius: "5px",
                  marginTop: "6px",
                }}
              >
                {getUserTypeText(user.userType || "")}
              </span>
            </div>
          </button>

          {menuOpen && (
            <div
              className="dropdown-menu dropdown-menu-end show mt-2 shadow-sm"
              style={{ right: 0 }}
            >
              <div className="d-md-none p-2 border-bottom">
                <span>{user.email}</span>
                <span>{user.name}</span>
                <span>{getUserTypeText(user.userType || "")}</span>
              </div>

              <Link href="/edit-profile" className="dropdown-item">
                <i className="bi bi-person me-2"></i> Perfil
              </Link>
              <div className="dropdown-divider"></div>
              <button className="dropdown-item text-danger" onClick={handleLogout}>
                <i className="bi bi-box-arrow-right me-2"></i> Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default TopBar;
