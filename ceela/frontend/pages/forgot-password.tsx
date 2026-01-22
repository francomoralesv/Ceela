import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import { useState } from "react";
import { useRouter } from "next/router";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";
import CustomButton from "../src/components/common/CustomButton";
import { NextPage } from "next";
import { ReactElement } from "react";
import Head from "next/head";

type NextPageWithLayout = NextPage & {
  getLayout?: (page: ReactElement) => ReactElement;
};


const ForgotPassword: NextPageWithLayout = () => {
  const [email, setEmail] = useState<string>("");
  const [sentEmail, setSentEmail] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch(`${constantUrlApiEndpoint}/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.message || "Error en el proceso de recuperación de contraseña"
        );
      }

      // Guarda el email enviado en un estado para mostrarlo
      setSentEmail(email);
      localStorage.setItem("reset_email", email);
      // Limpia el campo y cualquier mensaje previo
      setEmail("");
      setError(null);
      setSuccess(true);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error desconocido";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="forgot-password-container d-flex justify-content-center align-items-center"
      style={{
        height: "100vh",
        background: "url('/assets/images/login_background.png') no-repeat center center/cover",
        fontFamily: "var(--font-family-base)",
      }}
    >
      {/* Tarjeta blanca centradfdsa */}
      <div
        className="shadow"
        style={{
          width: "100%",
          maxWidth: "500px",
          borderRadius: "20px",
          backgroundColor: "#fff",
          padding: "3rem",
        }}
      >
        <h4
          style={{
            color: "var(--primary-color)",
            marginBottom: "0.5rem",
            fontFamily: "var(--font-family-base)",
            fontWeight: 500,
          }}
        >
          Recupera tu cuenta
        </h4>
        <p
          style={{
            color: "var(--muted-text)",
            marginBottom: "1.5rem",
            fontFamily: "var(--font-family-base)",
          }}
        >
          Ingresa tu email registrado
        </p>

        {/* Mensaje de error */}
        {error && (
          <p
            className="text-danger text-center fw-bold"
            style={{ marginBottom: "1rem" }}
          >
            {error}
          </p>
        )}

        {success ? (
          // Mensaje de éxito inline dentro del recuadro
          <div>
            <p
              style={{
                color: "green",
                textAlign: "center",
                marginBottom: "1.5rem",
                fontFamily: "var(--font-family-base)",
              }}
            >
              ¡El correo se ha enviado exitosamente a {sentEmail}! Revisa tu
              bandeja de entrada para continuar.
            </p>
            <CustomButton
              type="button"
              variant="save"
              className="btn btn-block w-100"
              onClick={() => router.push("/resetpassword")}
            >
              Continuar
            </CustomButton>
          </div>
        ) : (
          // Muestra el formulario si aún no se ha enviado con éxito
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label
                style={{
                  display: "block",
                  marginBottom: "0.5rem",
                  color: "#000",
                  fontFamily: "var(--font-family-base)",
                  fontWeight: 500,
                }}
              >
                Dirección de correo
              </label>
              <input
                type="email"
                className="form-control"
                placeholder="Example@gmail.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{height: "3rem"}}
              />
            </div>

            <div className="d-flex gap-3">
              <CustomButton
                type="button"
                variant="back"
                onClick={() => router.back()}
                color="red"
                style={{ height: "38px", display: "flex", alignItems: "center" }}
              >
                Cancelar
              </CustomButton>

              <CustomButton
                type="submit"
                variant="save"
                className="btn btn-block"
                disabled={isLoading}
                style={{ flex: "1", height: "38px", display: "flex", alignItems: "center", justifyContent: "center" }}
              >
                {isLoading ? (
                  <span>
                    <i className="bi bi-arrow-repeat spin"></i> Cargando...
                  </span>
                ) : (
                  "Recuperar contraseña"
                )}
              </CustomButton>
            </div>
          </form>
        )}
      </div>
      <style jsx>{`
        .spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
};

ForgotPassword.getLayout = function getLayout(page: ReactElement) {
  return (
    <>
      <Head>
        <title>Forgot Password</title>
      </Head>
      {page}
    </>
  );
};

export default ForgotPassword;