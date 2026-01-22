import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import { useState, useEffect } from "react";
import Head from "next/head";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";
import Image from "next/image";
import useAuth from "../src/hooks/useAuth";
import CustomButton from "@/components/common/CustomButton";
import Card from "../src/components/common/Card";
import { notify } from "@/utils/notify";
import Title from "../src/components/Title";
import Breadcrumb from "@/components/common/Breadcrumb";
import { useRouter } from "next/router";

interface ProfileData {
  name: string;
  lastname: string;
  number_phone: string;
  country: string;
  ubigeo: string;
  proffesion?: string; // Campo opcional
  userType?: string;  // Aquí se almacenará el ID del rol (ej. "1" o "2")
  email?: string;
}

// Función para convertir el ID de rol a texto (solo para mostrar en este componente)
const getUserTypeText = (roleId: string): string => {
  if (roleId === "1") return "Administrador";
  if (roleId === "2") return "Desarrollador";
  return "Desconocido";
};

const EditProfile = () => {
  useAuth();
  const router = useRouter();
  console.log("[EditProfile] Página cargada y sesión validada.");

  const [profile, setProfile] = useState<ProfileData>({
    name: "",
    lastname: "",
    number_phone: "",
    country: "",
    ubigeo: "",
    proffesion: "",
    userType: "",
    email: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedProfile = localStorage.getItem("userProfile");
    // Obtenemos el ID del rol desde localStorage
    const roleId = localStorage.getItem("role_id") || "";
    if (storedProfile) {
      try {
        const parsedProfile: ProfileData = JSON.parse(storedProfile);
        setProfile({
          name: parsedProfile.name || "",
          lastname: parsedProfile.lastname || "",
          number_phone: parsedProfile.number_phone || "",
          country: parsedProfile.country || "",
          ubigeo: parsedProfile.ubigeo || "",
          proffesion: parsedProfile.proffesion || "",
          userType: roleId,
          email: parsedProfile.email || "",
        });
        console.log("[EditProfile] Perfil cargado desde localStorage:", parsedProfile);
      } catch (err) {
        console.error("[EditProfile] Error al parsear el perfil desde localStorage", err);
      }
    } else {
      console.warn("[EditProfile] No se encontró información del perfil en localStorage.");
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const { name, lastname, number_phone, country, ubigeo } = profile;
    if (!name.trim() || !lastname.trim() || !number_phone.trim() || !country.trim() || !ubigeo.trim()) {
      notify("Por favor, complete todos los campos.");
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) throw new Error("No estás autenticado. Inicia sesión.");

      // No enviamos userType ni email al backend
      const payload = { ...profile };
      delete payload.userType;
      delete payload.email;

      console.log("[EditProfile] Enviando actualización del perfil:", payload);

      const response = await fetch(`${constantUrlApiEndpoint}/user/me/update`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || errorData.message || "No se pudo actualizar el perfil"
        );
      }

      await response.json();
      localStorage.setItem("userProfile", JSON.stringify({ ...profile }));
      notify("Tu perfil se actualizó correctamente.");

      // Dispara un evento para notificar a otros componentes del cambio
      window.dispatchEvent(new Event("profileUpdated"));

      router.back();
    } catch (err: unknown) {
      console.error("[EditProfile] Error actualizando perfil:", err);
      notify("Error al actualizar el perfil");
    } finally {
      setLoading(false);
    }
  };

  /** --- ESTILOS --- **/
  const baseFontSize = "1rem";

  const labelStyle = {
    marginBottom: "0.3rem",
    fontFamily: "var(--font-family-base)",
    fontWeight: 400,
    fontSize: baseFontSize,
    color: "#000",
  } as React.CSSProperties;

  const inputStyle = {
    width: "100%",
    border: "1px solid #eee",
    borderRadius: "8px",
    padding: "0.75rem 1rem",
    fontFamily: "var(--font-family-base)",
    fontSize: baseFontSize,
  };

  const fieldContainerStyle = {
    marginBottom: "1rem",
  };

  const boxStyle = {
    border: "1px solid #eee",
    borderRadius: "8px",
    padding: "1.2rem",
    display: "flex",
    flexDirection: "column" as const,
    gap: "0.5rem",
    flex: 1,
  };

  return (
    <>
      <Card>
        <div className="d-flex align-items-center w-100">
          <Title text="Editar Perfil" />
          <Breadcrumb
            items={[
              {
                title: "Editar Perfil",
                href: "/",
                active: true,
              },
            ]}
          />
        </div>
      </Card>
      <Head>
        <title>Editar Perfil</title>
      </Head>

      <div className="container-fluid p-0">
        <Card>
          <div className="row g-3" style={{ marginBottom: "6rem" }}>
            {/* Columna Izquierda (Perfil) */}
            <div className="col-md-4">
              <div style={boxStyle}>
                <h5
                  style={{
                    fontFamily: "var(--font-family-base)",
                    fontSize: "1.2rem",
                    marginBottom: "3rem",
                    fontWeight: 600,
                  }}
                >
                  Mi perfil
                </h5>

                <div className="d-flex align-items-center" style={{ gap: "1rem", marginBottom: "1rem" }}>
                  <div>
                    <Image
                      className="img-65 rounded-circle"
                      src="/assets/images/profile-placeholder.png"
                      alt="Profile"
                      width={60}
                      height={60}
                      style={{ objectFit: "cover" }}
                    />
                  </div>
                  <div style={{ fontSize: baseFontSize }}>
                    <div
                      style={{
                        fontSize: "1.5rem",
                        marginBottom: "0.2rem",
                        fontWeight: 600,
                      }}
                    >
                      {profile.name.toUpperCase() || "NOMBRES"} {profile.lastname.toUpperCase() || "APELLIDOS"}
                    </div>
                    <div style={{ fontSize: baseFontSize, color: "#666", marginBottom: "2rem" }}>
                      {getUserTypeText(profile.userType || "")}
                    </div>
                  </div>
                </div>

                <div style={{ marginBottom: "2rem" }}>
                  <label style={labelStyle}>
                    Email Address <span style={{ color: "red" }}></span>
                  </label>
                  <div style={{ fontSize: baseFontSize, color: "#666" }}>
                    {profile.email || "your-email@domain.com"}
                  </div>
                </div>

                <div style={{ marginBottom: "2rem" }}>
                  <label style={labelStyle}>
                    Password <span style={{ color: "red" }}></span>
                  </label>
                  <div style={{ fontSize: baseFontSize, color: "#666", marginBottom: "3.5rem" }}>
                    ********
                  </div>
                </div>
              </div>
            </div>

            {/* Columna Derecha (Formulario) */}
            <div className="col-md-8">
              <div style={boxStyle}>
                <h5
                  style={{
                    color: "#6dbdc9",
                    fontFamily: "var(--font-family-base)",
                    fontWeight: 600,
                    fontSize: "1.2rem",
                    marginBottom: "3.4rem",
                  }}
                >
                  Editar Perfil
                </h5>

                {error && (
                  <div className="alert alert-danger" style={{ marginBottom: "1rem", fontFamily: "var(--font-family-base)" }}>
                    {error}
                  </div>
                )}

                {loading ? (
                  <p className="text-primary">Cargando...</p>
                ) : (
                  <form onSubmit={handleSubmit} style={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
                    {/* Fila 1: Nombre - Apellidos */}
                    <div className="row g-2">
                      <div className="col-md-6" style={fieldContainerStyle}>
                        <label style={labelStyle}>
                          Nombre <span style={{ color: "red" }}>*</span>
                        </label>
                        <input
                          type="text"
                          name="name"
                          className="form-control"
                          value={profile.name}
                          onChange={handleChange}
                          style={inputStyle}
                        />
                      </div>
                      <div className="col-md-6" style={fieldContainerStyle}>
                        <label style={labelStyle}>
                          Apellidos <span style={{ color: "red" }}>*</span>
                        </label>
                        <input
                          type="text"
                          name="lastname"
                          className="form-control"
                          value={profile.lastname}
                          onChange={handleChange}
                          style={inputStyle}
                        />
                      </div>
                    </div>

                    {/* Fila 2: Teléfono - País */}
                    <div className="row">
                      <div className="col-md-6" style={fieldContainerStyle}>
                        <label style={labelStyle}>
                          Teléfono <span style={{ color: "red" }}>*</span>
                        </label>
                        <input
                          type="text"
                          name="number_phone"
                          className="form-control"
                          value={profile.number_phone}
                          onChange={handleChange}
                          style={inputStyle}
                        />
                      </div>
                      <div className="col-md-6" style={fieldContainerStyle}>
                        <label style={labelStyle}>
                          País <span style={{ color: "red" }}>*</span>
                        </label>
                        <input
                          type="text"
                          name="country"
                          className="form-control"
                          value={profile.country}
                          onChange={handleChange}
                          style={inputStyle}
                        />
                      </div>
                    </div>

                    {/* Fila 3: Ubigeo y Profesión */}
                    <div className="row">
                      <div className="col-md-6" style={fieldContainerStyle}>
                        <label style={labelStyle}>
                          Codigo postal <span style={{ color: "red" }}>*</span>
                        </label>
                        <input
                          type="text"
                          name="ubigeo"
                          className="form-control"
                          value={profile.ubigeo}
                          onChange={handleChange}
                          style={inputStyle}
                          placeholder="Ej. 150101"
                        />
                      </div>
                      <div className="col-md-6" style={fieldContainerStyle}>
                        <label style={labelStyle}>
                          Profesión
                        </label>
                        <input
                          type="text"
                          name="proffesion"
                          className="form-control"
                          value={profile.proffesion}
                          onChange={handleChange}
                          style={inputStyle}
                          placeholder="Ej. Ingeniero"
                        />
                      </div>
                    </div>

                    {/* Mensaje de campos obligatorios */}
                    <div style={{ fontSize: baseFontSize, marginBottom: "1rem" }}>
                      <span style={{ color: "red" }}>*</span> Campos obligatorios
                    </div>

                    <div className="mt-auto d-flex justify-content-between">
                      <CustomButton
                        type="button"
                        variant="back"
                        onClick={() => router.back()}
                        color="red"
                      >
                        Cancelar
                      </CustomButton>

                      <CustomButton
                        type="submit"
                        variant="save"
                        className="btn btn-primary"
                      >
                        Guardar
                      </CustomButton>
                    </div>
                  </form>
                )}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
};

export default EditProfile;
