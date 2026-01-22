import Navbar from "@/components/layout/Navbar";
import TopBar from "@/components/layout/TopBar";
import Footer from "@/components/layout/Footer";
import { RecintosProvider } from "@/context/RecintosContext";
import '@/styles/css/datatable-mobile.css';
import '@/styles/globals.css';
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/css/bootstrap.min.css";
import type { NextPage } from 'next';
import type { AppProps } from 'next/app';
import { useRouter } from "next/router";
import Script from 'next/script';
import 'public/assets/css/color-1.css';
import 'public/assets/css/font-awesome.css';
import 'public/assets/css/style.css';
import 'public/assets/css/vendors/animate.css';
import 'public/assets/css/vendors/bootstrap.css';
import 'public/assets/css/vendors/feather-icon.css';
import 'public/assets/css/vendors/flag-icon.css';
import 'public/assets/css/vendors/icofont.css';
import 'public/assets/css/vendors/owlcarousel.css';
import 'public/assets/css/vendors/scrollbar.css';
import 'public/assets/css/vendors/sweetalert2.css';
import 'public/assets/css/vendors/themify.css';
import type { ReactElement } from 'react';
import { useEffect, useState } from "react";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "../styles/layout.css";

type NextPageWithLayout = NextPage & {
  getLayout?: (page: ReactElement) => ReactElement;
};

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

function MyApp({ Component, pageProps }: AppPropsWithLayout) {
  const router = useRouter();
  const hideNavRoutes = ["/login", "/twofactorauth"];
  const showNav = !hideNavRoutes.includes(router.pathname);
  const [isNavbarOpen, setIsNavbarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Detectamos si es dispositivo móvil
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 1024);
    };

    if (typeof window !== 'undefined') {
      handleResize();
      window.addEventListener('resize', handleResize);
    }

    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('resize', handleResize);
      }
    };
  }, []);

  // Función para manejar el toggle de la navbar (se recibe desde el componente Navbar)
  const handleNavbarToggle = (isOpen: boolean) => {
    setIsNavbarOpen(isOpen);
  };

  // Definimos anchos para el estado colapsado y expandido para desktop.
  // En mobile el comportamiento permanece overlay, por ello el margen es 0.
  const collapsedWidth = "6.5em";
  const expandedWidth = "200px";
  const contentMarginLeft = !isMobile ? (isNavbarOpen ? expandedWidth : collapsedWidth) : "0";

  const getLayout = Component.getLayout ?? ((page) => {
    return (
      <>
        <Script src="/assets/js/icons/feather-icon/feather.min.js" />
        <RecintosProvider>
          <div className="page-wrapper" id="pageWrapper">
            <div
              className="page-header"
              style={{
                marginLeft: showNav ? (isMobile ? contentMarginLeft : (isNavbarOpen ? expandedWidth : collapsedWidth)) : "0",
                transition: "margin-left 0.3s ease"
              }}
            >
              <div className="header-wrapper row m-0">
                {showNav && <TopBar sidebarWidth={isNavbarOpen ? expandedWidth : collapsedWidth} />}
              </div>
            </div>
            <div className="page-body-wrapper horizontal-menu">
              <div className="sidebar-wrapper" data-layout="fill-svg">
                {showNav && (
                  <Navbar
                    setActiveView={() => { }}
                    onNavbarToggle={handleNavbarToggle}
                  />
                )}
              </div>
              <div
                className="page-body"
                style={{
                  marginLeft: showNav ? `calc(${contentMarginLeft} + 25px)` : "0",
                  transition: "margin-left 0.3s ease",
                  width: showNav ? `calc(100% - (${contentMarginLeft} + 25px))` : "100%",
                  paddingBottom: showNav ? "40px" : "0"
                }}
              >
                {!hideNavRoutes.includes(router.pathname) ? (
                  <div >
                    {page}
                  </div>
                ) : (
                  page
                )}
              </div>
            </div>
            {showNav && <Footer />}
          </div></RecintosProvider>
        <ToastContainer
          position="top-right"
          autoClose={2000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </>
    );
  });

  useEffect(() => {
    const loadClientSideLibraries = async () => {
      const { loadJQuery } = await import('@/utils/clientSideImports');
      await loadJQuery();
    };

    loadClientSideLibraries();
  }, []);

  return getLayout(<Component {...pageProps} />);
}

export default MyApp;
