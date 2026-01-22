'use client'
import "bootstrap/dist/css/bootstrap.min.css";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import React, { useEffect, useState, useRef } from "react";
import GoogleIcons from "../../../public/GoogleIcons";
import useIsClient from "../../utils/useIsClient";
import { constantUrlApiEndpoint } from "../../utils/constant-url-endpoint";

interface NavbarProps {
  setActiveView?: (view: string) => void;
  onNavbarToggle?: (isOpen: boolean) => void;
}

const Navbar: React.FC<NavbarProps> = ({ onNavbarToggle }) => {
  const router = useRouter();
  const [roleId, setRoleId] = useState<string | null>(null);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [isNavOpen, setIsNavOpen] = useState(false);
  const [isSubmenuOpen, setIsSubmenuOpen] = useState(false);
  const [isDataEntrySubmenuOpen, setIsDataEntrySubmenuOpen] = useState(false);
  const isClient = useIsClient();
  const navRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!isClient) return;
    const storedRole = localStorage.getItem("role_id");
    if (storedRole) {
      setRoleId(storedRole);
    }
  }, [isClient]);

  useEffect(() => {
    if (!isClient) return;
    const storedProjectId = localStorage.getItem("project_id");
    if (storedProjectId) {
      setProjectId(storedProjectId);
    }
  }, [isClient]);

  useEffect(() => {
    if (!isClient) return;
    const handleResize = () => {
      const mobile = window.innerWidth <= 1024;
      setIsMobile(mobile);
      if (mobile) {
        setIsNavOpen(false);
      }
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [isClient]);

  useEffect(() => {
    if (!isMobile || !isNavOpen) return;
    const handleClickOutside = (event: MouseEvent) => {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setIsNavOpen(false);
        if (onNavbarToggle) {
          onNavbarToggle(false);
        }
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, [isMobile, isNavOpen, onNavbarToggle]);

  useEffect(() => {
    if (
      router.pathname === "/workflow-part1-create" ||
      router.pathname === "/workflow-part2-create"
    ) {
      setIsSubmenuOpen(true);
    } else {
      setIsSubmenuOpen(false);
    }
  }, [router.pathname]);

  const handleLogout = async () => {
    if (!isClient) return;

    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    try {
      const response = await fetch(`${constantUrlApiEndpoint}/logout`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
          "token": token,
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

    localStorage.clear();
    router.push("/login");
  };

  const handleNewFunction = () => {
    setIsNavOpen((prev) => {
      const newState = !prev;
      if (onNavbarToggle) {
        onNavbarToggle(newState);
      }
      return newState;
    });
  };

  const navLinkStyle: React.CSSProperties = {
    cursor: "pointer",
    fontFamily: "var(--font-family-base)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center",
    width: "100%",
    padding: "10px 5px",
    marginBottom: "8px",
    boxSizing: "border-box",
    fontSize: "0.90rem",
    lineHeight: "1.3",
    whiteSpace: "normal",
    wordWrap: "break-word",
    transition: "all 0.3s ease",
    color: "#fff",
    fontWeight: "normal",
    borderRadius: "4px",
    opacity: 0.9,
  };

  const isActive = (path: string): boolean => {
    return router.pathname === path;
  };

  const isCreateProjectActive = (): boolean => {
    return router.pathname === "/workflow-part1-create" || 
           router.pathname === "/workflow-part2-create";
  };

  const isDevelopmentProjectActive = (): boolean => {
    return router.pathname === "/workflow-part2-create";
  };

  const navItemStyle = (path: string): React.CSSProperties => ({
    backgroundColor: isActive(path) ? "#FEBE1B" : "transparent",
    borderRadius: "4px",
    transition: "background-color 0.3s ease",
    margin: '2px 0',
    width: '100%', // Añadido para asegurar que ocupe todo el ancho
  });
  
  const submenuItemStyle = (isActive: boolean): React.CSSProperties => ({
    backgroundColor: isActive ? "#FEBE1B" : "transparent",
    borderRadius: "4px",
    transition: "background-color 0.3s ease",
    margin: '2px 0',
    width: '100%', // Añadido para asegurar que ocupe todo el ancho
  });

  const createProjectNavItemStyle: React.CSSProperties = {
    backgroundColor: isCreateProjectActive() ? "#FEBE1B" : "transparent",
    borderRadius: "4px",
    transition: "background-color 0.3s ease",
    width: '100%', // Añadido para asegurar que ocupe todo el ancho
  };

  const developmentNavItemStyle: React.CSSProperties = {
    backgroundColor: isDevelopmentProjectActive() ? "#FEBE1B" : "transparent",
    borderRadius: "4px",
    transition: "background-color 0.3s ease",
    width: '100%', // Añadido para asegurar que ocupe todo el ancho
  };

  const iconStyle = (): React.CSSProperties => ({
    fontSize: "1.5rem",
    marginBottom: isNavOpen ? 0 : "1px",
    color: "#fff",
    backgroundColor: "transparent",
    borderRadius: "50%",
    padding: "0.5rem",
    transition: "all 0.3s ease",
    width: "40px",
    height: "40px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    boxSizing: "border-box",
    flexShrink: 0, // Añadido para evitar que el icono se reduzca
  });

  const logoContainerStyle: React.CSSProperties = {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    width: "100%",
    minHeight: "100px",
    boxSizing: "border-box",
    padding: isMobile ? "1rem 0.5rem" : "1rem 0.5rem",
    marginBottom: "1rem",
    color: "#fff",
    background: "linear-gradient(to bottom, #ffffff 50%, var(--primary-color) 100%)",
    position: "relative",
    zIndex: 999,
  };

  const navbarWidth = isNavOpen
    ? (isMobile ? "12.5em" : "18em")
    : (isMobile ? "6em" : "8.5em");

  const desktopLogoWidth = 97;
  const desktopLogoHeight = 50;
  const mobileLogoWidth = 63;
  const mobileLogoHeight = 47;

  return (
    <>
      <GoogleIcons />

      {isMobile && !isNavOpen && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleNewFunction();
          }}
          style={{
            position: "fixed",
            top: "10px",
            left: "10px",
            zIndex: 1200,
            backgroundColor: "var(--primary-color)",
            border: "none",
            color: "#fff",
            width: "50px",
            height: "50px",
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer"
          }}
        >
          <span className="material-icons" style={{ fontSize: "1.5rem" }}>
            menu
          </span>
        </button>
      )}

      {(!isMobile || (isMobile && isNavOpen)) && (
        <nav
          ref={navRef}
          className="sidebar d-flex flex-column"
          style={{
            position: isMobile ? "fixed" : "absolute",
            top: 0,
            bottom: 0,
            left: 0,
            zIndex: 1200,
            width: navbarWidth,
            backgroundColor: "var(--primary-color)",
            fontFamily: "var(--font-family-base)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            transition: "all 0.3s ease",
            boxShadow: "2px 0 10px rgba(0, 0, 0, 0.1)",
            overflow: "hidden" // Añadido para evitar desbordamiento
          }}
        >
          <div style={logoContainerStyle}>
            <Image
              src={isNavOpen ? "/assets/images/ceela.png" : "/assets/images/logo-min.png"}
              alt="Logo"
              width={isNavOpen ? (isMobile ? mobileLogoWidth : desktopLogoWidth) : (isMobile ? 50 : 80)}
              height={isNavOpen ? (isMobile ? mobileLogoHeight : desktopLogoHeight) : (isMobile ? 60 : 75)}
              style={{ borderRadius: "0", zIndex: 1100 }}
            />
            {(!isMobile || (isMobile && isNavOpen)) && (
              <div
                className="navbar-toggle-inside"
                onClick={handleNewFunction}
                style={{
                  marginTop: "0.5rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: "40px",
                  height: "40px",
                  border: "none",
                  backgroundColor: "transparent"
                }}
              >
                <span
                  className="material-icons"
                  style={{ color: "white", fontSize: "1.5rem" }}
                >
                  menu
                </span>
              </div>
            )}
          </div>

          <div
            className="menu-container"
            style={{
              fontFamily: "var(--font-family-base)",
              display: "flex",
              flexDirection: "column",
              height: "100%",
              width: '100%', // Añadido para asegurar que ocupe todo el ancho
              overflowY: 'auto', // Añadido para scroll si es necesario
            }}
          >
            <ul className="nav flex-column" style={{ width: '100%' }}>
              {roleId === "1" ? (
                <>
                  {/* Sección General */}
                  <div className="nav-section" style={{ width: '100%' }}>
                    <div
                      style={{
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '0 20px',
                        marginBottom: '10px',
                        width: '100%',
                      }}
                    >
                      <span
                        style={{
                          color: "#fff",
                          fontSize: "0.8rem",
                          opacity: 0.7
                        }}
                      >
                        General
                      </span>
                    </div>
                    <div style={{ display: 'block', width: '100%' }}>
                      <li 
                        className={`nav-item ${isActive('/dashboard') ? 'active' : ''}`}
                        style={navItemStyle('/dashboard')}
                      >
                        <div
                          className="nav-link text-white"
                          style={{
                            ...navLinkStyle,
                            flexDirection: isNavOpen ? "row" : "column",
                            justifyContent: isNavOpen ? "flex-start" : "center",
                            padding: isNavOpen ? "10px 20px" : "10px 5px",
                            cursor: "pointer",
                          }}
                          onClick={() => {
                            router.push("/dashboard");
                          }}
                        >
                          <span
                            style={iconStyle()}
                            className="material-icons"
                          >
                            dashboard
                          </span>
                          {isNavOpen && (
                            <span style={{ marginLeft: "10px" }}>
                              1. Dashboard
                            </span>
                          )}
                        </div>
                      </li>
                      <li 
                        className={`nav-item ${isActive('/project-status') ? 'active' : ''}`}
                        style={navItemStyle('/project-status')}
                      >
                        <div
                          className="nav-link text-white"
                          style={{
                            ...navLinkStyle,
                            flexDirection: isNavOpen ? "row" : "column",
                            justifyContent: isNavOpen ? "flex-start" : "center",
                            padding: isNavOpen ? "10px 20px" : "10px 5px",
                            cursor: "pointer",
                          }}
                          onClick={() => {
                            router.push("/project-status");
                          }}
                        >
                          <span
                            style={iconStyle()}
                            className="material-icons"
                          >
                            folder
                          </span>
                          {isNavOpen && (
                            <span style={{ marginLeft: "10px" }}>
                              2. Proyectos
                            </span>
                          )}
                        </div>
                      </li>
                    </div>
                  </div>

                  {/* Sección Configuración */}
                  <div className="nav-section" style={{ marginTop: "20px", width: '100%' }}>
                    <div
                      style={{
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '0 10px',
                        marginBottom: '10px',
                        width: '100%',
                      }}
                    >
                      <span
                        style={{
                          color: "#fff",
                          fontSize: "0.9rem",
                          opacity: 0.7,
                        }}
                      >
                        Configuración
                      </span>
                    </div>
                    <div style={{ display: 'block', width: '100%' }}>
                      <li 
                        className={`nav-item ${isActive('/user-management') ? 'active' : ''}`}
                        style={navItemStyle('/user-management')}
                      >
                        <div
                          className="nav-link text-white"
                          style={{
                            ...navLinkStyle,
                            flexDirection: isNavOpen ? "row" : "column",
                            justifyContent: isNavOpen ? "flex-start" : "center",
                            padding: isNavOpen ? "10px 20px" : "10px 5px",
                            cursor: "pointer",
                          }}
                          onClick={() => {
                            router.push("/user-management");
                          }}
                        >
                          <span
                            style={iconStyle()}
                            className="material-icons"
                          >
                            people
                          </span>
                          {isNavOpen && (
                            <span style={{ marginLeft: "10px" }}>
                              3. Usuarios
                            </span>
                          )}
                        </div>
                      </li>
                      <li 
                        className={`nav-item ${isActive('/administration') ? 'active' : ''}`}
                        style={navItemStyle('/administration')}
                      >
                        <div
                          className="nav-link text-white"
                          style={{
                            ...navLinkStyle,
                            flexDirection: isNavOpen ? "row" : "column",
                            justifyContent: isNavOpen ? "flex-start" : "center",
                            padding: isNavOpen ? "10px 20px" : "10px 5px",
                            cursor: "pointer",
                          }}
                          onClick={() => {
                            router.push("/administration");
                          }}
                        >
                          <span
                            style={iconStyle()}
                            className="material-icons"
                          >
                            settings
                          </span>
                          {isNavOpen && (
                            <span style={{ marginLeft: "10px" }}>
                              4. Parámetros
                            </span>
                          )}
                        </div>
                      </li>
                    </div>
                  </div>
                </>
              ) : roleId === "2" && (
                <>
                  {/* Sección General */}
                  <div className="nav-section">
                    <div
                      style={{
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '0 20px',
                        marginBottom: '10px'
                      }}
                    >
                      <span
                        style={{
                          color: "#fff",
                          fontSize: "0.8rem",
                          opacity: 0.7
                        }}
                      >
                        General
                      </span>
                    </div>
                    <div style={{ display: 'block' }}>
                      <li 
                        className={`nav-item ${isActive('/data-entry') ? 'active' : ''}`}
                      >
                        <div
                          className="nav-link text-white"
                          style={{
                            ...navLinkStyle,
                            flexDirection: isNavOpen ? "row" : "column",
                            justifyContent: isNavOpen ? "flex-start" : "center",
                            padding: isNavOpen ? "10px 20px" : "10px 5px",
                            cursor: "pointer",
                            backgroundColor: isActive('/data-entry') ? "#FEBE1B" : "transparent",
                          }}
                          onClick={() => {
                            router.push("/data-entry?step=3");
                            setIsDataEntrySubmenuOpen((prev) => !prev);
                          }}
                        >
                          <span style={iconStyle()} className="material-icons">
                            input
                          </span>
                          <span
                            style={{
                              marginLeft: isNavOpen ? "10px" : "0",
                              display: !isMobile && !isNavOpen ? "none" : "block"
                            }}
                          >
                            1. Ingreso de Datos de entrada
                          </span>
                          {isNavOpen && (
                            <span
                              className="material-icons"
                              style={{
                                marginLeft: "auto",
                                transform: isDataEntrySubmenuOpen ? "rotate(180deg)" : "rotate(0deg)",
                                transition: "transform 0.3s ease",
                              }}
                            >
                              expand_more
                            </span>
                          )}
                        </div>
                        {isNavOpen && (
                          <div
                            style={{
                              maxHeight: isDataEntrySubmenuOpen ? "200px" : "0px",
                              opacity: isDataEntrySubmenuOpen ? 1 : 0,
                              overflow: "hidden",
                              transition: "all 0.3s ease",
                            }}
                          >
                            <ul className="nav flex-column" style={{ paddingLeft: "20px" }}>
                              <li 
                                className={`nav-item ${router.pathname === '/data-entry' && router.query.step === '3' ? 'active' : ''}`}
                                style={submenuItemStyle(router.pathname === '/data-entry' && router.query.step === '3')}
                              >
                                <Link
                                  href="/data-entry?step=3"
                                  className="nav-link text-white"
                                  style={{
                                    ...navLinkStyle,
                                    flexDirection: "row",
                                    justifyContent: "flex-start",
                                    padding: "10px 20px",
                                  }}
                                >
                                  <span style={iconStyle()} className="material-icons">
                                    imagesearch_roller
                                  </span>
                                  <span style={{ marginLeft: "10px", display: "block" }}>
                                    Lista de materiales
                                  </span>
                                </Link>
                              </li>
                              <li 
                                className={`nav-item ${router.pathname === '/data-entry' && router.query.step === '5' ? 'active' : ''}`}
                                style={submenuItemStyle(router.pathname === '/data-entry' && router.query.step === '5')}
                              >
                                <Link
                                  href="/data-entry?step=5"
                                  className="nav-link text-white"
                                  style={{
                                    ...navLinkStyle,
                                    flexDirection: "row",
                                    justifyContent: "flex-start",
                                    padding: "10px 20px",
                                  }}
                                >
                                  <span style={iconStyle()} className="material-icons">
                                    home
                                  </span>
                                  <span style={{ marginLeft: "10px", display: "block" }}>
                                    Ventanas y Puertas
                                  </span>
                                </Link>
                              </li>
                              <li 
                                className={`nav-item ${router.pathname === '/data-entry' && router.query.step === '6' ? 'active' : ''}`}
                                style={submenuItemStyle(router.pathname === '/data-entry' && router.query.step === '6')}
                              >
                                <Link
                                  href="/data-entry?step=6"
                                  className="nav-link text-white"
                                  style={{
                                    ...navLinkStyle,
                                    flexDirection: "row",
                                    justifyContent: "flex-start",
                                    padding: "10px 20px",
                                  }}
                                >
                                  <span style={iconStyle()} className="material-icons">
                                    deck
                                  </span>
                                  <span style={{ marginLeft: "10px", display: "block" }}>
                                    Perfil de uso
                                  </span>
                                </Link>
                              </li>
                            </ul>
                          </div>
                        )}
                      </li>
                    </div>
                  </div>
                  {/* Sección Proyecto */}
                  <div className="nav-section" style={{ marginTop: "20px" }}>
                    <div
                      style={{
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '0 20px',
                        marginBottom: '10px'
                      }}
                    >
                      <span
                        style={{
                          color: "#fff",
                          fontSize: "1rem",
                          opacity: 0.7
                        }}
                      >
                        Proyecto
                      </span>
                    </div>
                    <div style={{ display: 'block' }}>
                      <li 
                        className={`nav-item ${isActive('/project-list') ? 'active' : ''}`}
                        style={navItemStyle('/project-list')}
                      >
                        <Link
                          href="/project-list"
                          className="nav-link text-white"
                          style={{
                            ...navLinkStyle,
                            flexDirection: isNavOpen ? "row" : "column",
                            justifyContent: isNavOpen ? "flex-start" : "center",
                            padding: isNavOpen ? "10px 20px" : "10px 5px"
                          }}
                        >
                          <span
                            style={iconStyle()}
                            className="material-icons"
                          >
                            dns
                          </span>
                          <span
                            style={{
                              marginLeft: isNavOpen ? "10px" : "0",
                              display: !isMobile && !isNavOpen ? "none" : "block"
                            }}
                          >
                            2. Listado
                          </span>
                        </Link>
                      </li>

                      <li 
                        className={`nav-item ${isCreateProjectActive() ? 'active' : ''}`}
                        style={createProjectNavItemStyle}
                      >
                        <Link
                          href="/workflow-part1-create"
                          className="nav-link text-white"
                          style={{
                            ...navLinkStyle,
                            flexDirection: isNavOpen ? "row" : "column",
                            justifyContent: isNavOpen ? "flex-start" : "center",
                            padding: isNavOpen ? "10px 20px" : "10px 5px"
                          }}
                        >
                          <span
                            style={iconStyle()}
                            className="material-icons"
                          >
                            note_add
                          </span>
                          <span
                            style={{
                              marginLeft: isNavOpen ? "10px" : "0",
                              display: !isMobile && !isNavOpen ? "none" : "block"
                            }}
                          >
                            3. Crear Proyecto
                          </span>
                        </Link>
                      </li>
                    </div>
                  </div>
                </>
              )}
            </ul>

            <ul className="nav flex-column" style={{ marginTop: "auto", width: '100%' }}>
              <li 
                className={`nav-item ${isActive('/logout') ? 'active' : ''}`}
                style={navItemStyle('/logout')}
              >
                <div
                  className="nav-link text-white"
                  style={{
                    ...navLinkStyle,
                    flexDirection: isNavOpen ? "row" : "column",
                    justifyContent: isNavOpen ? "flex-start" : "center",
                    padding: isNavOpen ? "10px 20px" : "10px 5px",
                    cursor: "pointer"
                  }}
                  onClick={handleLogout}
                >
                  <span
                    style={iconStyle()}
                    className="material-icons"
                  >
                    logout
                  </span>
                  <span
                    style={{
                      marginLeft: isNavOpen ? "10px" : "0",
                      display: !isMobile && !isNavOpen ? "none" : "block"
                    }}
                  >
                    Salir
                  </span>
                </div>
              </li>
            </ul>
          </div>

          <style jsx>{`
            .sidebar {
              overflow-x: hidden;
            }
            .menu-container {
              width: 100%;
              flex: 1;
              background-color: var(--primary-color);
              padding: 0;
            }
            .sidebar .nav-link {
              font-size: 1.1rem !important;
            }
            .sidebar .nav-link .material-icons {
              font-size: 1.1rem !important;
            }
            .sidebar .nav-link span {
              font-size: 1.1rem !important;
            }
            .sidebar .material-icons {
              font-size: 1.1rem !important;
            }
            .sidebar span {
              font-size: 1.1rem !important;
            }
            .sidebar > .menu-container > .d-flex > ul > .nav-item:hover {
              background-color: #FEBE1B !important;
              transition: background-color 0.3s ease !important;
            }
            
            .sidebar .nav-item:hover {
              background-color: transparent !important;
            }
            @media (max-width: 1024px) {
              .sidebar {
                width: 50%;
              }
              .sidebar .nav-link {
                font-size: 0.9rem !important;
                padding: 3px;
              }
              .sidebar .nav-link .material-icons {
                font-size: 0.9rem !important;
                margin-bottom: 0;
              }
              .sidebar .nav-link span {
                font-size: 0.9rem !important;
              }
              .sidebar .material-icons {
                font-size: 0.9rem !important;
              }
              .sidebar span {
                font-size: 0.9rem !important;
              }
              .sidebar .nav-link:hover,
              .sidebar .nav-item:hover {
                background-color: #FEBE1B !important;
                transition: background-color 0.3s ease !important;
              }
              /* Style for active nav item */
              .sidebar > .menu-container > .d-flex > ul > .nav-item.active {
                background-color: #FEBE1B !important;
                border-radius: 4px;
              }
              
              .sidebar .nav-item.active {
                background-color: transparent !important;
              }
              
              .sidebar .nav-item.active > .nav-link {
                background-color: #FEBE1B !important;
                border-radius: 4px;
              }
              .sidebar .nav-item.active .nav-link {
                color: #000 !important;
              }
              .sidebar .nav-item.active .material-icons {
                color: #000 !important;
              }
            }
          `}</style>
        </nav>
      )}
    </>
  );
};

export default Navbar;