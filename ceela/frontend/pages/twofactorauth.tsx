import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";
import { useRouter } from "next/router";
import { useState, useEffect } from "react";
import CustomButton from "../src/components/common/CustomButton";
import Link from "next/link";
import Head from "next/head";
import { ReactElement } from "react";

// Definición del tipo para páginas con layout propio
type NextPageWithLayout = {
  getLayout?: (page: ReactElement) => ReactElement;
};

const TwoFactorAuth: NextPageWithLayout = () => {
  const [otp, setOtp] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    const storedEmail = localStorage.getItem("email");
    if (!storedEmail) {
      setError("No se encontró el email. Inicia sesión nuevamente.");
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } else {
      setEmail(storedEmail);
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    if (!email) {
      setError("El email no está definido. Vuelve a iniciar sesión.");
      setLoading(false);
      return;
    }

    const requestBody = { email, otp: otp.toString() };
    console.log("Enviando código al backend:", JSON.stringify(requestBody, null, 2));

    try {
      const response = await fetch(`${constantUrlApiEndpoint}/2fa-verify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      console.log("Respuesta completa del backend:", response);

      const data = await response.json();
      console.log("Respuesta del backend:", data);

      if (!response.ok) {
        console.error("Error en la verificación:", data);
        throw new Error(data.detail || "Código incorrecto.");
      }

      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        console.log("Token almacenado correctamente:", data.access_token);
      } else {
        console.error("No se recibió un token válido del backend.");
        throw new Error("No se pudo autenticar el usuario.");
      }

      if (data.user) {
        localStorage.setItem("userProfile", JSON.stringify(data.user));
        console.log("Perfil de usuario guardado correctamente:", data.user);

        // Guardar role_id en local storage
        if (data.user.role_id) {
          localStorage.setItem("role_id", data.user.role_id.toString());
          console.log("role_id almacenado correctamente:", data.user.role_id);
        } else {
          console.warn("No se encontró role_id en la respuesta del backend.");
        }
      } else {
        console.warn("No se recibió información de perfil del usuario.");
      }

      localStorage.setItem("isAuthenticated", "true");

      // Redireccionar basado en el role_id
      if (data.user && data.user.role_id) {
        if (data.user.role_id === 1) {
          router.push("/dashboard");
        } else if (data.user.role_id === 2) {
          router.push("/project-list");
        } else {
          // Si el role_id no es ni 1 ni 2, se redirige por defecto al dashboard
          router.push("/dashboard");
        }
      } else {
        router.push("/dashboard");
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error desconocido";
      console.error("Error en la verificación:", message);
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const otpInputStyle = {
    textAlign: "center" as const,
    fontSize: "2rem",
    fontWeight: "bold" as const,
    letterSpacing: "8px",
    width: "100%",
    padding: "15px",
    border: "2px solid var(--muted-text)",
    borderRadius: "10px",
    marginBottom: "1rem",
    fontFamily: "var(--font-family-base)",
  };

  const submitButtonOverride = {
    width: "100%",
  };

  const regresarButtonStyle = {
    border: "none",
    backgroundColor: "transparent",
    color: "var(--primary-color)",
    fontSize: "1rem",
    display: "inline-flex",
    alignItems: "center",
    gap: "0.5rem",
    cursor: "pointer",
    textDecoration: "none" as const,
    fontFamily: "var(--font-family-base)",
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "url('/assets/images/login_background.png') no-repeat center center/cover",
        fontFamily: "var(--font-family-base)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        className="card p-5 shadow-lg"
        style={{
          width: "100%",
          maxWidth: "420px",
          borderRadius: "15px",
          backgroundColor: "#fff",
        }}
      >
        <h5
          className="fw-bold text-center"
          style={{
            color: "var(--primary-color)",
            marginBottom: "0.5rem",
            fontFamily: "var(--font-family-base)",
          }}
        >
          Autenticación de Doble Factor
        </h5>
        <p
          className="text-muted text-center"
          style={{
            marginBottom: "1rem",
            fontFamily: "var(--font-family-base)",
          }}
        >
          Ingresa el código de 6 dígitos enviado a tu email.
        </p>
        {error && (
          <p
            className="text-danger text-center fw-bold"
            style={{ fontFamily: "var(--font-family-base)" }}
          >
            {error}
          </p>
        )}
        <form onSubmit={handleSubmit} className="form-auth">
          <input
            type="text"
            style={otpInputStyle}
            placeholder="******"
            maxLength={6}
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            required
            pattern="[0-9]{6}"
            inputMode="numeric"
          />
          <CustomButton
            type="submit"
            variant="save"
            disabled={loading}
            style={submitButtonOverride}
          >
            {loading ? "Verificando..." : "Confirmar Código"}
          </CustomButton>
        </form>
        <div style={{ textAlign: "center", marginTop: "1rem" }}>
          <Link href="/login" style={regresarButtonStyle}>
            Regresar
          </Link>
        </div>
      </div>
      <style jsx global>{`
        a:hover {
          color: var(--secondary-color);
        }
      `}</style>
    </div>
  );
};

TwoFactorAuth.getLayout = function getLayout(page: ReactElement) {
  return (
    <>
      <Head>
        <title>Two Factor Auth</title>
      </Head>
      {page}
    </>
  );
};

export default TwoFactorAuth;
