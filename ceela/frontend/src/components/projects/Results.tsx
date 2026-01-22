import { useApi } from "@/hooks/useApi";
import { notify } from "@/utils/notify";
import jsPDF from "jspdf";
import { Download } from "lucide-react";
import { useRouter } from "next/router";
import { memo, useEffect, useRef, useState } from "react";
import { Container, Spinner, Tab, Tabs } from "react-bootstrap";
import CustomButton from "../common/CustomButton";
import WebSocketComponent from "../common/WebSocketComponent";
import IndicadoresFinales from "./tabs/IndicadoresFinales";
import ResumenRecintos from "./tabs/ResumenRecintos";

const MemoizedResumenRecintos = memo(ResumenRecintos);

const Results = () => {
  const router = useRouter();
  const { get } = useApi(); const [loading, setLoading] = useState(true);
  const [isButtonDisabled, setIsButtonDisabled] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  // Commented out for now as it's not used
  // const [isRecalculating, setIsRecalculating] = useState(false);
  const webSocketRef = useRef<any>(null);

  const [calculationResult, setCalculationResult] = useState<any>(null);

  const processData = async () => {
    try {
      const projectId = router.query.id;
      if (projectId) {
        await get(`/calculator/${projectId}`);
        setIsButtonDisabled(false);
      }
    } catch (error: any) {
      if (error?.response?.status === 400 && error?.response?.data?.detail) {
        notify(error.response.data.detail, "error");
      } else {
        console.error("Error processing data:", error);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (router.query.id) {
      processData();
    }
  }, [router.query.id]);

  const handleUpdate = (data: any) => {
    console.log("GUARDANDO :", data);
    // Removed setRecintos usage
  };
  // Uncomment this function when recalculation functionality is needed
  /*
  const handleForceRecalculation = async () => {
    try {
      setIsRecalculating(true);
      // Limpiar notificaciones antes de recalcular
      webSocketRef.current?.clearNotifications?.();
      const projectId = router.query.id;
      if (projectId) {
        const result = await get(`/calculator/${projectId}?force_calculation=true`);
        setCalculationResult(result);
        notify("Recálculo completado exitosamente");
      }
    } catch (error: any) {
      if (error?.response?.status === 400 && error?.response?.data?.detail) {
        notify(error.response.data.detail, "error");
      } else {
        console.error("Error al forzar recálculo:", error);
        notify("Error al forzar recálculo", "error");
      }
    } finally {
      setIsRecalculating(false);
    }
  };
  */

  const api = useApi();
  const handleDownloadIndicatorsPDF = () => {
    if (!calculationResult?.final_indicators) {
      notify("No hay indicadores finales para exportar", "error");
      return;
    }
    const doc = new jsPDF();
    const indicators = calculationResult.final_indicators;
    const primaryColor = [42, 176, 197]; // Color primario turquesa
    const secondaryColor = [50, 120, 160]; // Color secundario azul
    const accentColor = [255, 140, 0]; // Naranja para acentos
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();



    // Título principal
    doc.setFont("helvetica", "bold");
    doc.setFontSize(24);
    doc.setTextColor(primaryColor[0], primaryColor[1], primaryColor[2]);
    doc.text("Resultados de Análisis Energético", pageWidth / 2, 33, { align: "center" });

    // Subtítulo
    doc.setFontSize(16);
    doc.setTextColor(80, 80, 80);
    doc.text("Indicadores de Desempeño", pageWidth / 2, 43, { align: "center" });

    // Fecha y metadatos
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(100);
    const fecha = new Date().toLocaleString();
    doc.text(`Fecha de generación: ${fecha}`, pageWidth - 14, 55, { align: "right" });

    // Nombre del proyecto (si está disponible)
    const projectName = localStorage.getItem("project_name") || "Proyecto";
    const region = localStorage.getItem("project_department") || "Región";
    doc.setFont("helvetica", "bold");
    doc.setTextColor(80, 80, 80);
    doc.text(`Proyecto: ${projectName}`, 14, 55); doc.setFont("helvetica", "normal");
    doc.text(`Región: ${region}`, 14, 62);

    // Línea divisoria
    doc.setDrawColor(...primaryColor as [number, number, number]);
    doc.setLineWidth(0.5);
    doc.line(14, 66, pageWidth - 14, 66);    // Sección de Demanda
    const drawDemandaTable = () => {
      doc.setFillColor(...primaryColor as [number, number, number]);
      doc.roundedRect(14, 77, pageWidth - 28, 8, 2, 2, 'F');
      doc.setTextColor(255);
      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.text("Demanda", 20, 82.5);

      // Subtítulos
      const demandaStartY = 86;
      doc.setTextColor(80, 80, 80);
      doc.setFontSize(10);
      doc.text("Concepto", 20, demandaStartY + 4);
      doc.text("[kWh/m2-año]", 85, demandaStartY + 4);
      doc.text("[kWh-año]", 130, demandaStartY + 4);
      doc.text("% Versus caso base", 175, demandaStartY + 4);

      // Líneas de división para encabezados
      doc.setLineWidth(0.2);
      doc.line(14, demandaStartY + 6, pageWidth - 14, demandaStartY + 6);

      // Datos
      doc.setFont("helvetica", "normal");
      const rowHeight = 7;

      // Calefacción
      doc.text("Calefacción", 20, demandaStartY + 4 + rowHeight);
      doc.text(indicators.demanda_calefaccion_final.toFixed(1), 85, demandaStartY + 4 + rowHeight);
      doc.text(indicators.demanda_calefaccion_final2.toFixed(1), 130, demandaStartY + 4 + rowHeight);
      doc.text(`${(indicators.demanda_calef_vs * 100).toFixed(1)}%`, 175, demandaStartY + 4 + rowHeight);

      // Refrigeración
      doc.text("Refrigeración", 20, demandaStartY + 4 + rowHeight * 2);
      doc.text(indicators.demanda_ref_final.toFixed(1), 85, demandaStartY + 4 + rowHeight * 2);
      doc.text(indicators.demanda_ref_final2.toFixed(1), 130, demandaStartY + 4 + rowHeight * 2);
      doc.text(`${(indicators.demanda_ref_vs * 100).toFixed(1)}%`, 175, demandaStartY + 4 + rowHeight * 2);

      // Iluminación
      doc.text("Iluminación", 20, demandaStartY + 4 + rowHeight * 3);
      doc.text(indicators.demanda_iluminacion_final.toFixed(1), 85, demandaStartY + 4 + rowHeight * 3);
      doc.text(indicators.demanda_iluminacion_final2.toFixed(1), 130, demandaStartY + 4 + rowHeight * 3);
      doc.text(`${(indicators.demanda_iluminacion_vs * 100).toFixed(1)}%`, 175, demandaStartY + 4 + rowHeight * 3);

      // Línea divisoria final
      doc.line(14, demandaStartY + 6 + rowHeight * 4, pageWidth - 14, demandaStartY + 6 + rowHeight * 4);

      return demandaStartY + 6 + rowHeight * 4 + 10; // Retorna la posición Y final + margen
    };    // Sección de Consumo Energía Primaria
    const drawConsumoTable = (startY: any) => {
      doc.setFillColor(...secondaryColor as [number, number, number]);
      doc.roundedRect(14, startY, pageWidth - 28, 8, 2, 2, 'F');
      doc.setTextColor(255);
      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.text("Consumo Energía Primaria", 20, startY + 5.5);

      // Subtítulos
      doc.setTextColor(80, 80, 80);
      doc.setFontSize(10);
      doc.text("Concepto", 20, startY + 14);
      doc.text("[kWh/m2-año]", 85, startY + 14);
      doc.text("[kWh-año]", 130, startY + 14);
      doc.text("% Versus caso base", 175, startY + 14);

      // Líneas de división para encabezados
      doc.setLineWidth(0.2);
      doc.line(14, startY + 16, pageWidth - 14, startY + 16);

      // Datos
      doc.setFont("helvetica", "normal");
      const rowHeight = 7;

      // Calefacción
      doc.text("Calefacción", 20, startY + 14 + rowHeight);
      doc.text(indicators.consumo_calefaccion_final.toFixed(1), 85, startY + 14 + rowHeight);
      doc.text(indicators.consumo_calefaccion_final2.toFixed(1), 130, startY + 14 + rowHeight);
      doc.text(`${(indicators.consumo_calef_vs * 100).toFixed(1)}%`, 175, startY + 14 + rowHeight);

      // Refrigeración
      doc.text("Refrigeración", 20, startY + 14 + rowHeight * 2);
      doc.text(indicators.consumo_refrigeracion_final.toFixed(1), 85, startY + 14 + rowHeight * 2);
      doc.text(indicators.consumo_refrigeracion_final2.toFixed(1), 130, startY + 14 + rowHeight * 2);
      doc.text(`${(indicators.consumo_ref_vs * 100).toFixed(1)}%`, 175, startY + 14 + rowHeight * 2);

      // Iluminación
      doc.text("Iluminación", 20, startY + 14 + rowHeight * 3);
      doc.text(indicators.consumo_iluminacion_final.toFixed(1), 85, startY + 14 + rowHeight * 3);
      doc.text(indicators.consumo_iluminacion_final2.toFixed(1), 130, startY + 14 + rowHeight * 3);
      doc.text(`${(indicators.consumo_iluminacion_vs * 100).toFixed(1)}%`, 175, startY + 14 + rowHeight * 3);

      // Línea divisoria final
      doc.line(14, startY + 16 + rowHeight * 4, pageWidth - 14, startY + 16 + rowHeight * 4);

      return startY + 16 + rowHeight * 4 + 10; // Retorna la posición Y final + margen
    };

    // Función para dibujar cuadros de indicadores Disconfort y CO2
    const drawIndicatorBoxes = (startY: any) => {
      const boxWidth = (pageWidth - 28 - 10) / 2; // Ancho de cada caja (con espacio entre ellas)

      // Caja de Hrs Disconfort
      doc.setFillColor(50, 150, 200);
      doc.roundedRect(14, startY, boxWidth, 8, 2, 2, 'F');
      doc.setTextColor(255);
      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.text("Hrs Disconfort T° libre", 20, startY + 5.5);

      // Datos de Disconfort
      doc.setTextColor(80, 80, 80);
      doc.setFontSize(11);
      doc.text("Total", 20, startY + 18);
      doc.setFont("helvetica", "bold");
      doc.text(`${indicators.disconfort_total.toFixed(1)} hrs/año`, boxWidth - 10, startY + 18, { align: "right" });

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.text("Comparación caso base", 20, startY + 26); doc.setFont("helvetica", "bold");
      doc.text(`${(indicators.disconfort_vs * 100).toFixed(1)}%`, boxWidth - 10, startY + 26, { align: "right" });

      // Caja de CO2 eq
      doc.setFillColor(...accentColor as [number, number, number]);
      doc.roundedRect(14 + boxWidth + 10, startY, boxWidth, 8, 2, 2, 'F');
      doc.setTextColor(255);
      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.text("CO₂ eq", 20 + boxWidth + 10, startY + 5.5);

      // Datos de CO2
      doc.setTextColor(80, 80, 80);
      doc.setFontSize(11);
      doc.text("Total", 20 + boxWidth + 10, startY + 18);
      doc.setFont("helvetica", "bold");
      doc.text(`${indicators.co2_eq_total.toFixed(1)} kg CO₂eq/año`, pageWidth - 24, startY + 18, { align: "right" });

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.text("Comparación caso base", 20 + boxWidth + 10, startY + 26);
      doc.setFont("helvetica", "bold");
      doc.text(`${(indicators.co2_eq_vs_caso_base * 100).toFixed(1)}%`, pageWidth - 24, startY + 26, { align: "right" });

      return startY + 30; // Retorna la posición Y final + margen
    };

    // Dibujar componentes en orden
    let currentY = 70;
    currentY = drawDemandaTable();
    currentY = drawConsumoTable(currentY);
    currentY = drawIndicatorBoxes(currentY);

    // Añadir pie de página con información de la aplicación
    doc.setFillColor(240, 240, 240);
    doc.rect(0, pageHeight - 20, pageWidth, 20, 'F');

    doc.setFontSize(9);
    doc.setTextColor(100);
    doc.setFont("helvetica", "normal");
    doc.text("Generado por Plataforma de Proyectos de Eficiencia Energética", pageWidth / 2, pageHeight - 12, { align: "center" });
    doc.text(`© ${new Date().getFullYear()} - Todos los derechos reservados`, pageWidth / 2, pageHeight - 6, { align: "center" });

    doc.save(`indicadores_finales_${projectName.replace(/\s+/g, '_')}.pdf`);
  };

  return (
    <Container fluid className="py-4">
      <h2 className="mb-4 mt-2">Resultados finales</h2>
      <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
        {/*<CustomButton*/}
        {/*  onClick={handleForceRecalculation}*/}
        {/*  className="mb-3"*/}
        {/*  disabled={isRecalculating}*/}
        {/*>*/}
        {/*  <RefreshCw size={18} style={{ marginRight: 8 }} />*/}
        {/*  Forzar recálculo*/}
        {/*</CustomButton>*/}        {/* Recalculating status indicator - uncomment when needed
        {isRecalculating && (
          <span style={{ minWidth: 120, display: "flex", alignItems: "center", gap: 8 }}>
            <Spinner animation="border" size="sm" role="status" />
            <span>Recalculando...</span>
          </span>
        )}
        */}
        <CustomButton
          color="orange"
          onClick={async () => {
            setIsButtonDisabled(true);
            setIsDownloading(true);
            try {
              const projectId = router.query.id;
              const response = await api.get(`/calculator/download/${projectId}`, {
                responseType: "blob",
              });
              const blob = response;
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `${projectId}_files.zip`;
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
              notify("Archivos descargados exitosamente.");
              setIsDownloading(false);
              setIsButtonDisabled(false);
            } catch (error) {
              console.error("Error al descargar los archivos:", error);
              notify("Error al descargar los archivos", "error");
              setIsDownloading(false);
              setIsButtonDisabled(false);
            }
          }}
          className="mb-3"
          disabled={isButtonDisabled}
        >
          <Download size={18} style={{ marginRight: 8 }} />
          Descargar archivos procesados
        </CustomButton>
        {isDownloading && (
          <span style={{ minWidth: 120, display: "flex", alignItems: "center", gap: 8 }}>
            <Spinner animation="border" size="sm" role="status" />
            <span>Descargando...</span>
          </span>
        )}       
         <CustomButton
          onClick={handleDownloadIndicatorsPDF}
          className="mb-3"
          style={{ marginLeft: 8, background: '#2a80c5' }}
        >
          <Download size={18} style={{ marginRight: 8 }} />
          Descargar PDF Indicadores Finales
        </CustomButton>
      </div>

      <WebSocketComponent
        ref={webSocketRef}
        path={``}
        onMessageReceived={(message) => {
          if (message?.notificationType == "result") {
            const enclosures = message?.payload?.result_by_enclosure_v2 || "";
            const baseEnclosures = JSON.parse(message?.payload?.base_by_enclosure_v2 || "[]");
            const finalIndicators = message?.payload?.final_indicators;

            setCalculationResult({
              result_by_enclosure_v2: enclosures,
              base_by_enclosure_v2: baseEnclosures,
              final_indicators: finalIndicators,
            });
          }
        }}
      />
      <br />
      {loading || !calculationResult ? (
        <div className="text-center" style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
          <Spinner animation="border" role="status" style={{ marginBottom: 8 }} />
          <span>Procesando datos, espere unos minutos</span>
        </div>
      ) : (
        <>
          <Tabs
            defaultActiveKey="recintos"
            id="results-tabs"
            className="mb-4 custom-tabs"
            style={{
              "--bs-nav-tabs-link-active-color": "var(--primary-color)",
              "--bs-nav-link-font-weight": "normal",
              fontFamily: "var(--font-family-base)",
              border: "none",
              "--bs-nav-link-color": "#bbc4cb",
              "--bs-nav-link-hover-color": "rgb(42, 176, 197)",
              "--bs-nav-tabs-link-hover-border-color": "transparent",
              "--bs-nav-tabs-link-active-border-color":
                "transparent transparent rgb(42, 176, 197) transparent",
              "--bs-nav-tabs-border-width": "3px",
              "--bs-nav-tabs-border-radius": "0px",
              "--bs-nav-link-padding-x": "10px",
              "--bs-nav-link-padding-y": "10px",
            } as React.CSSProperties}
          >
            <Tab eventKey="recintos" title="Resumen de Recintos">
              <MemoizedResumenRecintos
                globalResults={calculationResult}
                onUpdated={handleUpdate}
              />
            </Tab>
            <Tab eventKey="indicadores" title="Indicadores Finales">
              <IndicadoresFinales finalIndicators={calculationResult?.final_indicators} />
            </Tab>
          </Tabs>
        </>
      )}
    </Container>
  );
};

export default Results;
