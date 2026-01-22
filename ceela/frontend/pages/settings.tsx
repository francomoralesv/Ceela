import { useState, useEffect, ChangeEvent, FormEvent } from "react";
import { useRouter } from "next/router";
import Swal from "sweetalert2";
import Navbar from "../src/components/layout/Navbar";
import TopBar from "../src/components/layout/TopBar";
import CustomButton from "../src/components/common/CustomButton";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";
import useAuth from "../src/hooks/useAuth";

interface CustomizationData {
  primary_color: string;
  secondary_color: string;
  background_color: string;
  btn_save_bg: string;
  btn_save_hover_bg: string;
  btn_back_bg: string;
  btn_back_hover_bg: string;
  btn_delete_bg: string;
  btn_delete_hover_bg: string;
  logo?: File | null;
}

const SettingsPage = () => {
  useAuth();
  console.log("[SettingsPage] Página cargada y sesión validada.");

  const router = useRouter();
  const [customization, setCustomization] = useState<CustomizationData>({
    primary_color: "#3ca7b7",
    secondary_color: "#bbc4cb",
    background_color: "#fff",
    btn_save_bg: "#3ca7b7",
    btn_save_hover_bg: "#359ea7",
    btn_back_bg: "#6b7280",
    btn_back_hover_bg: "#4b5563",
    btn_delete_bg: "#ef4444",
    btn_delete_hover_bg: "#dc2626",
    logo: null,
  });
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarWidth, ] = useState("300px");



  useEffect(() => {
    const fetchCustomization = async () => {
      setFetching(true);
      try {
        console.log("[fetchCustomization] Obteniendo configuración...");
        const token = localStorage.getItem("token");
        if (!token) {
          throw new Error("No estás autenticado. Inicia sesión.");
        }
        const response = await fetch(
          `${constantUrlApiEndpoint}/customization`,
          {
            method: "GET",
            headers: {
              accept: "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(
            errorData.detail ||
              errorData.message ||
              "Error al obtener configuración"
          );
        }
        const data = await response.json();
        console.log("[fetchCustomization] Configuración recibida:", data);
        setCustomization({
          primary_color: data.primary_color || "#3ca7b7",
          secondary_color: data.secondary_color || "#bbc4cb",
          background_color: data.background_color || "#f9f5f5",
          btn_save_bg: data.btn_save_bg || "#3ca7b7",
          btn_save_hover_bg: data.btn_save_hover_bg || "#359ea7",
          btn_back_bg: data.btn_back_bg || "#6b7280",
          btn_back_hover_bg: data.btn_back_hover_bg || "#4b5563",
          btn_delete_bg: data.btn_delete_bg || "#ef4444",
          btn_delete_hover_bg: data.btn_delete_hover_bg || "#dc2626",
          logo: null,
        });
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : "Error al obtener la configuración";
        console.error("[fetchCustomization] Error:", message);
        setError(message);
      } finally {
        setFetching(false);
      }
    };

    fetchCustomization();
  }, []);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    console.log(`[handleChange] ${e.target.name} cambiado a:`, e.target.value);
    setCustomization({
      ...customization,
      [e.target.name]: e.target.value,
    });
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      console.log("[handleFileChange] Logo seleccionado:", e.target.files[0]);
      setCustomization({
        ...customization,
        logo: e.target.files[0],
      });
    }
  };

  const uploadLogo = async (): Promise<string | null> => {
    if (!customization.logo) return null;
    const formData = new FormData();
    formData.append("logo", customization.logo);
    try {
      const token = localStorage.getItem("token");
      console.log("[uploadLogo] Subiendo logo...");
      const response = await fetch(`/api/upload-logo`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Error al subir logo");
      }
      const resData = await response.json();
      console.log("[uploadLogo] Logo subido. URL:", resData.logoUrl);
      return resData.logoUrl;
    } catch (error: unknown) {
      console.error("[uploadLogo] Error:", error);
      return null;
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    const {
      primary_color,
      secondary_color,
      background_color,
      btn_save_bg,
      btn_save_hover_bg,
      btn_back_bg,
      btn_back_hover_bg,
      btn_delete_bg,
      btn_delete_hover_bg,
    } = customization;
    if (
      !primary_color.trim() ||
      !secondary_color.trim() ||
      !background_color.trim() ||
      !btn_save_bg.trim() ||
      !btn_save_hover_bg.trim() ||
      !btn_back_bg.trim() ||
      !btn_back_hover_bg.trim() ||
      !btn_delete_bg.trim() ||
      !btn_delete_hover_bg.trim()
    ) {
      Swal.fire({
        title: "Campos incompletos",
        text: "Por favor, completa los campos obligatorios.",
        icon: "warning",
        confirmButtonText: "Aceptar",
      });
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("No estás autenticado. Inicia sesión.");
      }

      if (customization.logo) {
        const logoUrl = await uploadLogo();
        if (logoUrl) {
          localStorage.setItem("logoUrl", logoUrl);
        }
      }

      console.log("[handleSubmit] Enviando configuración actualizada:", customization);
      const response = await fetch(`/api/update-styles`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          primary_color,
          secondary_color,
          background_color,
          btn_save_bg,
          btn_save_hover_bg,
          btn_back_bg,
          btn_back_hover_bg,
          btn_delete_bg,
          btn_delete_hover_bg,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("[handleSubmit] Error actualizando CSS:", errorData);
        throw new Error(
          errorData.detail ||
            errorData.message ||
            "No se pudo actualizar la configuración"
        );
      }

      const resData = await response.json();
      console.log("[handleSubmit] Configuración actualizada:", resData);


      await Swal.fire({
        title: "Configuración actualizada",
        text: resData.message || "La configuración se actualizó correctamente.",
        icon: "success",
        confirmButtonText: "Aceptar",
      });
      router.push("/dashboard");
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Error al actualizar la configuración";
      console.error("[handleSubmit] Error:", message);
      Swal.fire({
        title: "Error",
        text: message,
        icon: "error",
        confirmButtonText: "Aceptar",
      });
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const ColorPickerInput = ({
    label,
    name,
    value,
    onChange,
  }: {
    label: string;
    name: string;
    value: string;
    onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  }) => (
    <div className="mb-3" style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
      <label style={{ fontFamily: "var(--font-family-base)", minWidth: "200px" }}>
        {label} *
      </label>
      <input
        type="color"
        name={name}
        value={value}
        onChange={onChange}
        style={{ width: "50px", height: "50px", padding: 0, border: "none", background: "none" }}
      />
      <input
        type="text"
        name={name}
        value={value.toUpperCase()}
        onChange={onChange}
        style={{
          fontFamily: "var(--font-family-base)",
          width: "100px",
          height: "40px",
          textAlign: "center",
          border: "1px solid #ccc",
          borderRadius: "4px",
        }}
      />
      <div
        style={{
          width: "30px",
          height: "30px",
          backgroundColor: value,
          border: "1px solid #ccc",
        }}
      />
    </div>
  );

  return (
    <div className="d-flex" style={{ fontFamily: "var(--font-family-base)" }}>
      <Navbar setActiveView={() => {}} />
      <div className="d-flex flex-column flex-grow-1" style={{ marginLeft: sidebarWidth, width: "100%" }}>
        <TopBar sidebarWidth={sidebarWidth} />
        <div className="container p-4" style={{ marginTop: "80px" }}>
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2
              className="fw-bold"
              style={{
                color: "var(--primary-color)",
                margin: 0,
                fontFamily: "var(--font-family-base)",
              }}
            >
              Configuración de Personalización
            </h2>
            <div className="d-flex" style={{ gap: "1rem" }}>
              <CustomButton variant="back" onClick={() => router.push("/dashboard")}>
                ← Regresar
              </CustomButton>
              <CustomButton variant="save" type="submit" form="settingsForm" disabled={loading}>
                {loading ? "Guardando..." : "Guardar"}
              </CustomButton>
            </div>
          </div>
          {loading || fetching ? (
            <p className="text-primary" style={{ fontFamily: "var(--font-family-base)" }}>
              Cargando configuración...
            </p>
          ) : (
            <form id="settingsForm" onSubmit={handleSubmit} style={{ fontFamily: "var(--font-family-base)" }}>
              {error && (
                <p className="text-danger" style={{ fontFamily: "var(--font-family-base)" }}>
                  {error}
                </p>
              )}
              <ColorPickerInput
                label="Color Primario"
                name="primary_color"
                value={customization.primary_color}
                onChange={handleChange}
              />
              <ColorPickerInput
                label="Color Secundario"
                name="secondary_color"
                value={customization.secondary_color}
                onChange={handleChange}
              />
              <ColorPickerInput
                label="Color de Fondo"
                name="background_color"
                value={customization.background_color}
                onChange={handleChange}
              />
              <h3 style={{ fontFamily: "var(--font-family-base)", marginTop: "2rem" }}>
                Colores de Botones
              </h3>
              <ColorPickerInput
                label="Botón Guardar (fondo)"
                name="btn_save_bg"
                value={customization.btn_save_bg}
                onChange={handleChange}
              />
              <ColorPickerInput
                label="Botón Guardar (hover)"
                name="btn_save_hover_bg"
                value={customization.btn_save_hover_bg}
                onChange={handleChange}
              />
              <ColorPickerInput
                label="Botón Regresar (fondo)"
                name="btn_back_bg"
                value={customization.btn_back_bg}
                onChange={handleChange}
              />
              <ColorPickerInput
                label="Botón Regresar (hover)"
                name="btn_back_hover_bg"
                value={customization.btn_back_hover_bg}
                onChange={handleChange}
              />
              <ColorPickerInput
                label="Botón Borrar (fondo)"
                name="btn_delete_bg"
                value={customization.btn_delete_bg}
                onChange={handleChange}
              />
              <ColorPickerInput
                label="Botón Borrar (hover)"
                name="btn_delete_hover_bg"
                value={customization.btn_delete_hover_bg}
                onChange={handleChange}
              />
              <div className="mb-3">
                <label style={{ fontFamily: "var(--font-family-base)" }}>Logo</label>
                <input
                  type="file"
                  name="logo"
                  accept="image/png, image/jpeg"
                  className="form-control"
                  onChange={handleFileChange}
                  style={{ fontFamily: "var(--font-family-base)" }}
                />
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
