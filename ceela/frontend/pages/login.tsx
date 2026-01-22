import { NextPage } from "next";
import Head from "next/head";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { ReactElement, useEffect, useState } from "react";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";

type NextPageWithLayout = NextPage & {
  getLayout?: (page: ReactElement) => ReactElement;
};

const Login: NextPageWithLayout = () => {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [remember, setRemember] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const router = useRouter();

  // Verifica si el usuario está logueado y redirige a /dashboard
  useEffect(() => {
    const token = localStorage.getItem("token");
    const roleId = localStorage.getItem("role_id");

    if (token) {
      if (roleId === "1") {
        router.push("/dashboard");
      } else {
        router.push("/project-list");
      }
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const requestBody = { email, password };

    try {
      const response = await fetch(`${constantUrlApiEndpoint}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      console.log(response)

      const data = await response.json();

      if (data?.detail) {
        throw new Error(data?.detail)
      }
      if (!response.ok) {
        // Usa 'detail' si existe, de lo contrario 'message', 'error', etc.
        throw new Error(data.detail || data.message || data.error || "Credenciales incorrectas.");
      }


      // Si la respuesta es exitosa, guardamos datos y redirigimos
      localStorage.setItem("User", data.token);
      localStorage.setItem("email", email);
      localStorage.setItem("user_name", data.name || "Usuario");

      console.log("User data", data);
      setTimeout(() => {
        router.push("/twofactorauth");
      }, 200);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error desconocido";
      console.error("Error al iniciar sesión:", message);
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="container-fluid"
      style={{
        background: "url('/assets/images/login_background.png') no-repeat center center/cover",
      }}
    >
      <div className="row">
        <div className="col-12 p-0">
          <div className="login-card login-dark">
            <div>
              <div className="login-main">
                <div className="col-12 p-0 d-flex justify-content-center">
                  <Image
                    src="/assets/images/ceela.png"
                    alt="Ceela Logo"
                    width={120}
                    height={120}
                    className="img-fluid mt-4 mb-3"
                    style={{ objectFit: "contain" }}
                  />
                </div>
                <br />
                <hr />
                <form className="theme-form" onSubmit={handleSubmit}>
                  <h4 style={{ color: "var(--primary-color)" }}>
                    Ingresa a tu cuenta
                  </h4>
                  <p>Ingresa tu email y contraseña para iniciar sesión</p>

                  {error && <p className="text-danger text-center fw-bold">{error}</p>}

                  <div className="form-group">
                    <label className="col-form-label">Dirección de correo</label>
                    <input
                      type="email"
                      className="form-control"
                      placeholder="Test@gmail.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="col-form-label">Contraseña</label>
                    <div className="form-input position-relative">
                      <input
                        type={showPassword ? "text" : "password"}
                        className="form-control"
                        placeholder="********"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                      />
                      <div
                        className="show-hide"
                        style={{ cursor: "pointer", color: "var(--primary-color)" }}
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? "Ocultar" : "Mostrar"}
                      </div>
                    </div>
                  </div>

                  <div className="form-group mb-0">
                    {/* Comentado temporalmente
                    <div className="form-check mb-2">
                      <input
                        id="remember"
                        className="form-check-input"
                        type="checkbox"
                        checked={remember}
                        onChange={(e) => setRemember(e.target.checked)}
                      />
                      <label className="form-check-label text-muted" htmlFor="remember">
                        Recuerdame
                      </label>
                    </div>
                    */}

                    <Link
                      href="/forgot-password"
                      className="d-block text-center mb-3"
                      style={{ color: "var(--primary-color)" }}
                    >
                      ¿Olvidaste tu contraseña?
                    </Link>

                    <button
                      className="btn w-100"
                      type="submit"
                      disabled={loading}
                      style={{
                        backgroundColor: "var(--primary-color)",
                        borderColor: "var(--primary-color)",
                        color: "#fff",
                      }}
                    >
                      {loading ? "Ingresando..." : "Iniciar sesión"}
                    </button>
                  </div>

                  <p className="mt-4 mb-0 text-center">
                    ¿No tienes cuenta?
                    <Link
                      style={{ color: "var(--primary-color)" }}
                      className="ms-2"
                      href="/register"
                    >
                      Crear cuenta
                    </Link>
                  </p>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

Login.getLayout = function getLayout(page: React.ReactElement) {
  return (
    <>
      <Head>
        <title>Login</title>
      </Head>
      {page}
    </>
  );
};

export default Login;