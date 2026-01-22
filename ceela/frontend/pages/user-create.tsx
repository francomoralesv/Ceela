import { useState } from "react";
import { useRouter } from "next/router";
import { constantUrlApiEndpoint } from "../src/utils/constant-url-endpoint";
import useAuth from "../src/hooks/useAuth";
import Card from "@/components/common/Card";
import Title from "@/components/Title";
import CreateButton from "@/components/CreateButton";
import { notify } from "@/utils/notify"; 
import Breadcrumb from "../src/components/common/Breadcrumb";

interface UserFormData {
  name: string;
  lastname: string;
  email: string;
  number_phone: string;
  birthdate: string;
  country: string;
  ubigeo: string;
  password: string;
  confirm_password: string;
  role_id: string;
}

const UserCreate = () => {
  // Validar sesión
  useAuth();
  console.log("[UserCreate] Página cargada y sesión validada.");

  const router = useRouter();
  const [userData, setUserData] = useState<UserFormData>({
    name: "",
    lastname: "",
    email: "",
    number_phone: "",
    birthdate: "",
    country: "",
    ubigeo: "",
    password: "",
    confirm_password: "",
    role_id: "2",
  });
  const [loading, setLoading] = useState(false);
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{ [key: string]: string }>({});

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    let value = e.target.value;

    // Filtrar caracteres para el campo "number_phone"
    if (e.target.name === "number_phone") {
      // Permitir solo dígitos, +, -, paréntesis y espacios
      value = value.replace(/[^0-9+\-\(\)\s]/g, "");
    }

    // Filtrar caracteres para el campo "ubigeo"
    if (e.target.name === "ubigeo") {
      // Permitir solo dígitos
      value = value.replace(/[^0-9]/g, "");
    }

    console.log(`[handleChange] ${e.target.name} cambiado a:`, value);
    setUserData({ ...userData, [e.target.name]: value });

    // Si el usuario modifica el campo, se remueve el error en ese campo (para otros errores)
    if (fieldErrors[e.target.name]) {
      setFieldErrors({ ...fieldErrors, [e.target.name]: "" });
    }
    // También se limpia el error general
    if (generalError) {
      setGeneralError(null);
    }
  };

  // Función auxiliar para renderizar el label con asterisco si el campo está vacío
  const renderLabel = (label: string, fieldName: keyof UserFormData) => (
    <>
      {label}{" "}
      {userData[fieldName].trim() === "" && (
        <span style={{ color: "red" }}>*</span>
      )}
    </>
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);
    // Validar campos requeridos: si alguno está vacío, se evita el envío (solo se muestra el asterisco en el label)
    const requiredFields: (keyof UserFormData)[] = [
      "name",
      "lastname",
      "email",
      "number_phone",
      "birthdate",
      "country",
      "ubigeo",
      "password",
      "confirm_password",
      "role_id",
    ];

    const missingFields = requiredFields.filter(
      (field) => !userData[field].trim()
    );
    if (missingFields.length > 0) {
      notify("Por favor complete todos los campos requeridos."); // Notificamos si faltan campos
      return;
    }

    // Validar que las contraseñas coincidan
    if (
      userData.password.trim() &&
      userData.confirm_password.trim() &&
      userData.password !== userData.confirm_password
    ) {
      setFieldErrors({ confirm_password: "Las contraseñas no coinciden." });
      notify("Las contraseñas no coinciden."); // Notificamos el error
      return;
    } else {
      setFieldErrors({});
    }

    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) {
        const errMsg = "No estás autenticado. Inicia sesión nuevamente.";
        notify(errMsg);
        throw new Error(errMsg);
      }
      const bodyToSend = {
        ...userData,
        role_id: Number(userData.role_id),
      };

      console.log("[handleSubmit] Enviando datos al backend:", bodyToSend);

      const resp = await fetch(`${constantUrlApiEndpoint}/register-admin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(bodyToSend),
      });

      if (!resp.ok) {
        const errorData = await resp.json();
        console.error("[handleSubmit] Servidor devolvió un error:", errorData);
        const message =
          errorData.detail || errorData.message || "No se pudo crear el usuario";
        // Si el error está relacionado al correo, se muestra debajo del campo email
        if (
          message.toLowerCase().includes("correo") ||
          message.toLowerCase().includes("email")
        ) {
          setFieldErrors((prev) => ({
            ...prev,
            email:
              "El correo ingresado ya se encuentra registrado. Por favor, use otro correo.",
          }));
        } else {
          setGeneralError(message);
        }
        notify(message); // Notificamos el error recibido
        return;
      }

      // Notificamos el éxito de la operación
      notify("Usuario creado exitosamente.");
      // Redirigir sin alerta de éxito
      router.push("/user-management");
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Error al crear usuario";
      console.error("[handleSubmit] Error:", message);
      setGeneralError(message);
      notify(message); // Notificamos el error capturado
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div>
        {/* Card para el Título */}
        <Card>
          <div className="d-flex align-items-center w-100">
            <Title text="Creación de usuario" />
            <Breadcrumb
              items={[
                {
                  title: "Creación de Usuario",
                  href: "/",
                  active: true,
                },
              ]}
            />
          </div>
        </Card>

        {/* Card para el Formulario */}
        <div>
          {generalError && (
            <p
              className="text-danger fw-bold"
              style={{ fontFamily: "var(--font-family-base)" }}
            >
              {generalError}
            </p>
          )}

          <Card>
            {loading ? (
              <p
                className="text-primary"
                style={{ fontFamily: "var(--font-family-base)" }}
              >
                Cargando...
              </p>
            ) : (
              <form id="userCreateForm" onSubmit={handleSubmit}>
                <div className="row">
                  <div className="col-md-6">
                    <label>{renderLabel("Nombre", "name")}</label>
                    <input
                      type="text"
                      name="name"
                      className="form-control"
                      value={userData.name}
                      onChange={handleChange}
                    />
                    {/* No se muestran mensajes de error para campos vacíos */}
                  </div>
                  <div className="col-md-6">
                    <label>{renderLabel("Apellidos", "lastname")}</label>
                    <input
                      type="text"
                      name="lastname"
                      className="form-control"
                      value={userData.lastname}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="row mt-3">
                  <div className="col-md-6">
                    <label>{renderLabel("Email", "email")}</label>
                    <input
                      type="email"
                      name="email"
                      className="form-control"
                      value={userData.email}
                      onChange={handleChange}
                    />
                    {fieldErrors.email && (
                      <small className="text-danger d-block">
                        {fieldErrors.email}
                      </small>
                    )}
                  </div>
                  <div className="col-md-6">
                    <label>{renderLabel("Teléfono", "number_phone")}</label>
                    <input
                      type="text"
                      name="number_phone"
                      className="form-control"
                      value={userData.number_phone}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="row mt-3">
                  <div className="col-md-6">
                    <label>{renderLabel("Fecha de Nacimiento", "birthdate")}</label>
                    <input
                      type="date"
                      name="birthdate"
                      className="form-control"
                      value={userData.birthdate}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="col-md-6">
                    <label>{renderLabel("País", "country")}</label>
                    <input
                      type="text"
                      name="country"
                      className="form-control"
                      value={userData.country}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="row mt-3">
                  <div className="col-md-6">
                    <label>{renderLabel("Contraseña", "password")}</label>
                    <input
                      type="password"
                      name="password"
                      className="form-control"
                      value={userData.password}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="col-md-6">
                    <label>{renderLabel("Codigo Postal", "ubigeo")}</label>
                    <input
                      type="text"
                      name="ubigeo"
                      className="form-control"
                      value={userData.ubigeo}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="row mt-3">
                  <div className="col-md-6">
                    <label>{renderLabel("Confirmar Contraseña", "confirm_password")}</label>
                    <input
                      type="password"
                      name="confirm_password"
                      className="form-control"
                      value={userData.confirm_password}
                      onChange={handleChange}
                    />
                    {fieldErrors.confirm_password && (
                      <small className="text-danger d-block">
                        {fieldErrors.confirm_password}
                      </small>
                    )}
                  </div>
                  <div className="col-md-6">
                    <label>{renderLabel("Rol", "role_id")}</label>
                    <select
                      name="role_id"
                      className="form-control"
                      value={userData.role_id}
                      onChange={handleChange}
                    >
                      <option value="1">Administrador</option>
                      <option value="2">Desarrollador</option>
                    </select>
                  </div>
                </div>

                {/* Mensaje de campos obligatorios */}
                <div className="d-flex justify-content-between align-items-center mt-4">
                  <p style={{ textAlign: "left", margin: 0 }}>
                    (<span style={{ color: "red" }}>*</span>) Campos Obligatorios
                  </p>

                  <CreateButton
                    backRoute="/user-management"
                    saveTooltip="Guardar Usuario"
                    saveText="Guardar" />
                </div>
              </form>
            )}
          </Card>
        </div>
      </div>

      <style jsx>{`
        .card {
          background: #fff;
          border-radius: 12px;
          box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
          border: none;
        }

        .custom-create-btn {
          background-color: var(--primary-color) !important;
          border: none !important;
          border-radius: 0.5rem !important;
          padding: 12px !important;
          font-size: 1rem !important;
          transition: background 0.3s ease !important;
          color: #fff !important;
          cursor: pointer;
          font-family: var(--font-family-base) !important;
        }
        .custom-create-btn:hover {
          background-color: var(--secondary-color) !important;
        }
      `}</style>
    </div>
  );
};

export default UserCreate;
