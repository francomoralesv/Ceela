import "bootstrap/dist/css/bootstrap.min.css";
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Swal from "sweetalert2";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";
import Link from "next/link";
import Head from "next/head";
import { ReactElement } from "react";

// Definición del tipo para páginas con layout propio
type NextPageWithLayout = {
  getLayout?: (page: ReactElement) => ReactElement;
};

const ResetPassword: NextPageWithLayout = () => {
  const [formData, setFormData] = useState({
    email: "",
    code: "",
    new_password: "",
    confirm_new_password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Estados para mostrar/ocultar contraseñas
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  useEffect(() => {
    const storedEmail = localStorage.getItem("reset_email");
    if (storedEmail) {
      setFormData((prevData) => ({ ...prevData, email: storedEmail }));
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.new_password !== formData.confirm_new_password) {
      setError("Las contraseñas no coinciden");
      return;
    }

    try {
      const response = await fetch(`${constantUrlApiEndpoint}/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || "Error al restablecer la contraseña");
      }

      // Mostrar alerta de éxito con SweetAlert2 y redireccionar
      await Swal.fire({
        icon: "success",
        title: "Contraseña cambiada exitosamente",
        showConfirmButton: false,
        timer: 2000,
        customClass: {
          popup: "rounded-swal",
        },
      });
      router.push("/login");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error desconocido";
      setError(message);
    }
  };

  // Estilos base
  const baseFontSize = "0.875rem";

  const inputContainerStyle = {
    position: "relative" as const,
    display: "flex",
    alignItems: "center",
  };

  const inputStyle = {
    width: "100%",
    border: "2px solid var(--muted-text)",
    borderRadius: "0.5rem",
    padding: "0.5rem",
    fontFamily: "var(--font-family-base)",
    paddingRight: "70px", // espacio para el texto de Mostrar/Ocultar
  };

  const labelStyle = {
    marginBottom: "1rem",
    fontWeight: 400,
    color: "var(--text-color)",
    fontFamily: "var(--font-family-base)",
    fontSize: baseFontSize,
  };

  const regresarButtonStyle = {
    border: "none",
    backgroundColor: "transparent",
    color: "var(--primary-color)",
    fontSize: baseFontSize,
    cursor: "pointer",
    textDecoration: "none" as const,
    fontFamily: "var(--font-family-base)",
  };

  // Estilo para el correo, dándole un toque más elegante
  const emailStyle = {
    fontFamily: "var(--font-family-base)",
    fontSize: "1.2rem",
    fontWeight: 500,
    color: "var(--primary-color)",
    textAlign: "center" as const,
    display: "block",
  };

  // Estilo para el contenedor que encierra el correo
  const emailBoxStyle = {
    marginBottom: "1rem",
    border: "1px solid var(--muted-text)",
    borderRadius: "0.5rem",
    padding: "0.5rem",
  };

  // Estilo para el texto "Mostrar/Ocultar"
  const toggleTextStyle = {
    position: "absolute" as const,
    right: "10px",
    top: "50%",
    transform: "translateY(-50%)",
    cursor: "pointer",
    fontFamily: "var(--font-family-base)",
    fontSize: baseFontSize,
    color: "var(--primary-color)",
    userSelect: "none" as const,
  };

  return (
    <div
      className="d-flex justify-content-center align-items-center"
      style={{
        minHeight: "100vh",
        background:
          "url('/assets/images/background.jpg') no-repeat center center/cover",
        fontFamily: "var(--font-family-base)",
      }}
    >
      <div
        className="card p-4 shadow"
        style={{
          width: "100%",
          maxWidth: "400px",
          borderRadius: "15px",
          backgroundColor: "#fff",
          border: "1px solid #eee",
        }}
      >
        {/* Título */}
        <h4
          className="text-start"
          style={{
            color: "var(--primary-color)",
            fontWeight: 400,
            marginBottom: "0.25rem",
          }}
        >
          Restablecer contraseña
        </h4>

        {/* Instrucciones */}
        <p
          style={{
            fontFamily: "var(--font-family-base)",
            color: "var(--text-color)",
            marginBottom: "1rem",
            textAlign: "left",
          }}
        >
          Ingresa tu código de verificación y tu nueva contraseña
        </p>

        {/* Contenedor del correo */}
        <div style={emailBoxStyle}>
          <span style={emailStyle}>{formData.email}</span>
          <p
            style={{
              fontFamily: "var(--font-family-base)",
              color: "var(--muted-text)",
              fontSize: baseFontSize,
              margin: 0,
              textAlign: "center",
            }}
          >
            Este es el correo asociado a tu cuenta.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Código de verificación */}
          <div className="mb-3">
            <label className="form-label" style={labelStyle}>
              Código de verificación
            </label>
            <input
              type="text"
              className="form-control"
              name="code"
              placeholder="Código recibido"
              value={formData.code}
              onChange={handleChange}
              required
              style={{ ...inputStyle, paddingRight: "0.5rem" }}
            />
          </div>

          {/* Nueva contraseña */}
          <div className="mb-3">
            <label className="form-label" style={labelStyle}>
              Nueva contraseña
            </label>
            <div style={inputContainerStyle}>
              <input
                type={showNewPassword ? "text" : "password"}
                className="form-control"
                name="new_password"
                placeholder="••••••••"
                value={formData.new_password}
                onChange={handleChange}
                required
                style={inputStyle}
              />
              <span
                style={toggleTextStyle}
                onClick={() => setShowNewPassword(!showNewPassword)}
              >
                {showNewPassword ? "Ocultar" : "Mostrar"}
              </span>
            </div>
          </div>

          {/* Confirmar contraseña */}
          <div className="mb-3">
            <label className="form-label" style={labelStyle}>
              Confirmar contraseña
            </label>
            <div style={inputContainerStyle}>
              <input
                type={showConfirmPassword ? "text" : "password"}
                className="form-control"
                name="confirm_new_password"
                placeholder="••••••••"
                value={formData.confirm_new_password}
                onChange={handleChange}
                required
                style={inputStyle}
              />
              <span
                style={toggleTextStyle}
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? "Ocultar" : "Mostrar"}
              </span>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary w-100 submit-btn"
            style={{
              
              border: "none",
              transition: "background 0.3s ease",
              color: "#fff",
              fontFamily: "var(--font-family-base)",
            }}
          >
            Restablecer contraseña
          </button>
        </form>

        {error && (
          <p
            className="text-danger text-center mt-3"
            style={{ fontFamily: "var(--font-family-base)", fontSize: baseFontSize }}
          >
            {error}
          </p>
        )}

        <div className="text-center mt-3">
          <Link href="/login" style={regresarButtonStyle}>
            ← Regresar
          </Link>
        </div>
      </div>

      <style jsx global>{`
        .submit-btn {
          background-color: var(--primary-color) !important;
        }
        .swal2-popup.rounded-swal {
          border-radius: 1rem !important;
        }
      `}</style>
    </div>
  );
};

ResetPassword.getLayout = function getLayout(page: ReactElement) {
  return (
    <>
      <Head>
        <title>Reset Password</title>
      </Head>
      {page}
    </>
  );
};

export default ResetPassword;
