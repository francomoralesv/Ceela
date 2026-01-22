// ConstructiveDetailsComponent.tsx
import DetailModal from "@/components/constructive_details/DetailModal";
import NewDetailCreator from "@/components/constructive_details/NewDetailCreator";
import TablesParameters from "@/components/tables/TablesParameters";
import { notify } from "@/utils/notify";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { useRouter } from "next/router";
import React, { useCallback, useEffect, useState } from "react";
import { constantUrlApiEndpoint } from "../utils/constant-url-endpoint";
import ActionButtonsConfirm from "./common/ActionButtonsConfirm";
import CustomButton from "./common/CustomButton";
import HorizontalTabs from "./common/HorizontalTabs";
import ModalCreate from "./common/ModalCreate";
import SearchParameters from "./inputs/SearchParameters";

interface Detail {
  id_detail: number;
  scantilon_location: string;
  name_detail: string;
  material_id: number;
  material: string;
  layer_thickness: number;
  created_status?: string;
}

export interface TabItem {
  code_ifc?: string;
  id_detail?: number;
  id?: number;
  name_detail: string;
  value_u?: number;
  created_status?: string;
  info?: {
    surface_color?: {
      exterior?: { name: string; value?: number };
      interior?: { name: string; value?: number };
    };
    aislacion_bajo_piso?: {
      lambda?: number;
      e_aisl?: number;
    };
    ref_aisl_vertical?: {
      lambda?: number;
      e_aisl?: number;
      d?: number;
    };
    ref_aisl_horizontal?: {
      lambda?: number;
      e_aisl?: number;
      d?: number;
    };
  };
  scantilon_location?: string;
  material?: string;
  layer_thickness?: number;
}

interface Material {
  id: number;
  name: string;
}

interface Constant {
  create_status: string;
  name: string;
  type: string;
  id: number;
  atributs: {
    name: string;
    density: number;
    conductivity: number;
    specific_heat: number;
  };
  is_deleted: boolean;
}

type TabStep4 = "detalles" | "muros" | "techumbre" | "pisos";

const getCssVarValue = (varName: string, fallback: string): string => {
  if (typeof window === "undefined") return fallback;
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(varName)
    .trim();
  return value || fallback;
};

const ConstructiveDetailsComponent: React.FC = () => {
  const router = useRouter();

  const [hasLoaded, setHasLoaded] = useState(false);
  const [primaryColor, setPrimaryColor] = useState("#3ca7b7");
  const [searchQuery, setSearchQuery] = useState("");

  const [fetchedDetails, setFetchedDetails] = useState<Detail[]>([]);
  const [showTabsInStep4, setShowTabsInStep4] = useState(true);
  const [tabStep4, setTabStep4] = useState<TabStep4>("detalles");

  const [murosTabList, setMurosTabList] = useState<TabItem[]>([]);
  const [techumbreTabList, setTechumbreTabList] = useState<TabItem[]>([]);
  const [pisosTabList, setPisosTabList] = useState<TabItem[]>([]);

  const [materials, setMaterials] = useState<Material[]>([]);

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingDetail, setDeletingDetail] = useState<Detail | null>(null);
  const [editingDetail, setEditingDetail] = useState<Detail | null>(null);

  const [showInlineDeleteModal, setShowInlineDeleteModal] = useState(false);
  const [deletingInlineDetail, setDeletingInlineDetail] =
    useState<TabItem | null>(null);

  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<{
    id: number;
    name_detail: string;
  } | null>(null);

  const [editingRowId, setEditingRowId] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<any>({});

  useEffect(() => {
    setPrimaryColor(getCssVarValue("--primary-color", "#3ca7b7"));
    setHasLoaded(true);
  }, []);

  const getToken = (): string | null => {
    const token = localStorage.getItem("token");
    if (!token) {
      notify("Token no encontrado", "Inicia sesión.");
    }
    return token;
  };

  const fetchData = useCallback(
    async <T,>(endpoint: string, setter: (data: T) => void) => {
      const token = getToken();
      if (!token) return;
      try {
        const { data } = await axios.get<T>(endpoint, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setter(data);
      } catch (error: unknown) {
        console.error(`Error al obtener datos desde ${endpoint}:`, error);
      }
    },
    []
  );

  const fetchFetchedDetails = useCallback(async () => {
    const token = getToken();
    if (!token) return;
    try {
      const url = `${constantUrlApiEndpoint}/admin/details/`;
      const { data } = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setFetchedDetails(data || []);
    } catch (error: unknown) {
      console.error("Error al obtener detalles:", error);
      notify("Error", "Error al obtener detalles. Ver consola.");
    }
  }, []);

  const fetchMurosDetails = useCallback(() => {
    fetchData<TabItem[]>(
      `${constantUrlApiEndpoint}/details/all/Muro/`,
      (data) => {
        setMurosTabList(data);
      }
    );
  }, [fetchData]);

  const fetchTechumbreDetails = useCallback(() => {
    fetchData<TabItem[]>(
      `${constantUrlApiEndpoint}/details/all/Techo/`,
      (data) => {
        setTechumbreTabList(data);
      }
    );
  }, [fetchData]);

  const fetchPisosDetails = useCallback(() => {
    fetchData<TabItem[]>(
      `${constantUrlApiEndpoint}/details/all/Piso/`,
      (data) => {
        setPisosTabList(data);
      }
    );
  }, [fetchData]);

  const fetchMaterials = async () => {
    const token = getToken();
    if (!token) return;
    try {
      const url = `${constantUrlApiEndpoint}/admin/constants/?page=1&per_page=700`;
      const { data } = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const allConstants: Constant[] = data.constants || [];
      const materialsList: Material[] = allConstants
        .filter(
          (c: Constant) =>
            c.name === "materials" && c.type === "definition materials"
        )
        .map((c: Constant) => ({
          id: c.id,
          name: c.atributs.name,
        }));
      setMaterials(materialsList);
    } catch (error: unknown) {
      console.error("Error al obtener materiales:", error);
      notify("Error", "Error al obtener Materiales.");
    }
  };

  useEffect(() => {
    if (hasLoaded) fetchFetchedDetails();
  }, [hasLoaded, fetchFetchedDetails]);

  useEffect(() => {
    if (showTabsInStep4) setTabStep4("muros");
  }, [showTabsInStep4]);

  useEffect(() => {
    if (showTabsInStep4 && hasLoaded) {
      if (tabStep4 === "muros") fetchMurosDetails();
      else if (tabStep4 === "techumbre") fetchTechumbreDetails();
      else if (tabStep4 === "pisos") fetchPisosDetails();
    }
  }, [
    showTabsInStep4,
    tabStep4,
    fetchMurosDetails,
    fetchTechumbreDetails,
    fetchPisosDetails,
    hasLoaded,
  ]);

  useEffect(() => {
    if (
      editingDetail &&
      editingDetail.material &&
      (!editingDetail.material_id || editingDetail.material_id === 0) &&
      materials.length > 0
    ) {
      const foundMaterial = materials.find(
        (mat) => mat.name.toLowerCase() === editingDetail.material.toLowerCase()
      );
      if (foundMaterial) {
        setEditingDetail({ ...editingDetail, material_id: foundMaterial.id });
      }
    }
  }, [editingDetail, materials]);

  const refreshDetails = async () => {
    await fetchFetchedDetails();
    if (tabStep4 === "muros") await fetchMurosDetails();
    else if (tabStep4 === "techumbre") await fetchTechumbreDetails();
    else if (tabStep4 === "pisos") await fetchPisosDetails();
  };

  const confirmDeleteDetail = async () => {
    if (!deletingDetail) return;
    const token = getToken();
    if (!token) {
      notify("Token no encontrado", "Inicia sesión.");
      return;
    }
    try {
      const url = `${constantUrlApiEndpoint}/admin/details/${deletingDetail.id_detail}/delete`;
      await axios.delete(url, {
        headers: {
          Authorization: `Bearer ${token}`,
          accept: "application/json",
        },
      });
      notify("Detalle correctamente eliminado");
      await fetchFetchedDetails();
      const tipo = deletingDetail.scantilon_location.toLowerCase();
      if (tipo === "muro") fetchMurosDetails();
      else if (tipo === "techo") fetchTechumbreDetails();
      else if (tipo === "piso") fetchPisosDetails();
    } catch (error: unknown) {
      console.error("Error al eliminar detalle:", error);
      notify("Error", "No se pudo eliminar el detalle.");
    } finally {
      setShowDeleteModal(false);
      setDeletingDetail(null);
      setShowDetailsModal(true);
    }
  };

  const handleInlineDeleteModal = (item: TabItem, e: React.MouseEvent) => {
    e.stopPropagation();
    setDeletingInlineDetail(item);
    setShowInlineDeleteModal(true);
  };

  const confirmInlineDeleteDetail = async () => {
    if (!deletingInlineDetail) return;
    const token = getToken();
    if (!token) return;
    try {
      const url = `${constantUrlApiEndpoint}/admin/${deletingInlineDetail.id}/details/delete`;
      await axios.delete(url, {
        headers: {
          Authorization: `Bearer ${token}`,
          accept: "application/json",
        },
      });
      notify("Detalle eliminado correctamente.");
      await fetchFetchedDetails();
      if (tabStep4 === "muros") fetchMurosDetails();
      else if (tabStep4 === "techumbre") fetchTechumbreDetails();
      else if (tabStep4 === "pisos") fetchPisosDetails();
    } catch (error: any) {
      console.error("Error al eliminar detalle inline:", error);
      notify("Error al eliminar el detalle.");
    } finally {
      setShowInlineDeleteModal(false);
      setDeletingInlineDetail(null);
    }
  };

  const handleEditDetail = (detail: Detail, e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDetailsModal(false);
    fetchMaterials();
    setEditingDetail(detail);
  };

  const handleConfirmEditDetail = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!editingDetail) return;
    if (
      !editingDetail.scantilon_location.trim() ||
      !editingDetail.name_detail.trim()
    ) {
      notify(
        "Los campos 'Ubicación Detalle' y 'Nombre Detalle' no pueden estar vacíos."
      );
      return;
    }
    if (!editingDetail.material_id || editingDetail.material_id <= 0) {
      notify("Por favor, seleccione un material válido.");
      return;
    }
    if (
      editingDetail.layer_thickness === null ||
      editingDetail.layer_thickness <= 0
    ) {
      notify("El 'Espesor de la capa' debe ser un valor mayor a 0.");
      return;
    }
    const token = getToken();
    if (!token) return;
    (async () => {
      try {
        const url = `${constantUrlApiEndpoint}/admin/details/${editingDetail.id_detail}/update`;
        const payload = {
          scantilon_location: editingDetail.scantilon_location,
          name_detail: editingDetail.name_detail,
          material_id: editingDetail.material_id,
          layer_thickness: editingDetail.layer_thickness,
        };
        await axios.put(url, payload, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
        notify("Actualizado con éxito.");
        await fetchFetchedDetails();
        const tipo = editingDetail.scantilon_location.toLowerCase();
        if (tipo === "muro") fetchMurosDetails();
        else if (tipo === "techo") fetchTechumbreDetails();
        else if (tipo === "piso") fetchPisosDetails();
        setEditingDetail(null);
        setShowDetailsModal(true);
      } catch (error: unknown) {
        console.error("Error al actualizar el detalle:", error);
        notify("Error al actualizar el detalle.");
      }
    })();
  };

  const handleInlineEdit = (item: TabItem, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingRowId(item.id_detail ?? item.id ?? null);
    setEditValues({
      name_detail: item.name_detail,
      exterior: item.info?.surface_color?.exterior?.name || "",
      interior: item.info?.surface_color?.interior?.name || "",
      vertLambda: item.info?.ref_aisl_vertical?.lambda || "",
      vertEAisl: item.info?.ref_aisl_vertical?.e_aisl || "",
      vertD: item.info?.ref_aisl_vertical?.d || "",
      horizLambda: item.info?.ref_aisl_horizontal?.lambda || "",
      horizEAisl: item.info?.ref_aisl_horizontal?.e_aisl || "",
      horizD: item.info?.ref_aisl_horizontal?.d || "",
    });
  };

  const handleInlineCancel = (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setEditingRowId(null);
    setEditValues({});
  };

  const handleInlineSave = async (
    item: TabItem,
    detailType: "Muro" | "Techo" | "Piso",
    e?: React.MouseEvent
  ) => {
    e?.stopPropagation();
    const token = getToken();
    if (!token) return;
    try {
      let url = `${constantUrlApiEndpoint}/${item.id_detail}/details/update`;
      let payload;
      if (detailType === "Piso") {
        payload = {
          name_detail: editValues.name_detail,
          info: {
            ref_aisl_vertical: {
              d: editValues.vertD !== "" ? editValues.vertD : null,
              e_aisl: editValues.vertEAisl !== "" ? editValues.vertEAisl : null,
              lambda:
                editValues.vertLambda !== "" ? editValues.vertLambda : null,
            },
            ref_aisl_horizontal: {
              d: editValues.horizD !== "" ? editValues.horizD : null,
              e_aisl:
                editValues.horizEAisl !== "" ? editValues.horizEAisl : null,
              lambda:
                editValues.horizLambda !== "" ? editValues.horizLambda : null,
            },
          },
        };
        url = `${constantUrlApiEndpoint}/${item.id}/details/update/Piso`;
      } else {
        payload = {
          name_detail: editValues.name_detail,
          info: {
            surface_color: {
              interior: { name: editValues.interior },
              exterior: { name: editValues.exterior },
            },
          },
        };
        url = `${constantUrlApiEndpoint}/${item.id}/details/update/${detailType}`;
      }
      await axios.put(url, payload, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      notify("Actualizado con éxito.");
      if (detailType === "Muro") fetchMurosDetails();
      else if (detailType === "Techo") fetchTechumbreDetails();
      else if (detailType === "Piso") fetchPisosDetails();
      handleInlineCancel();
    } catch (error: any) {
      console.error("Error al actualizar detalle inline:", error);
      notify("Ya existe un detalle con el nombre asignado.");
    }
  };

  /** Devuelve una copia filtrada de un array por nombre, colores, U-value, etc. */
  const searchFilter = (items: TabItem[]) => {
    if (!searchQuery.trim()) return items; // sin texto → no filtra
    const q = searchQuery.toLowerCase();
    return items.filter((it) =>
      [
        it.name_detail,
        it.value_u,
        it.info?.surface_color?.exterior?.name,
        it.info?.surface_color?.interior?.name,
        it.info?.aislacion_bajo_piso?.lambda,
        it.info?.ref_aisl_vertical?.lambda,
        it.info?.ref_aisl_horizontal?.lambda,
      ]
        .map((v) => (v ?? "").toString().toLowerCase())
        .some((s) => s.includes(q))
    );
  };

  const renderInitialDetails = (inModal: boolean = false) => {
    const columnsDetails = [
      { headerName: "Ubicación Detalle", field: "scantilon_location" },
      { headerName: "Nombre Detalle", field: "name_detail" },
      { headerName: "Material", field: "material" },
      { headerName: "Espesor capa (cm)", field: "layer_thickness" },
      { headerName: "Acciones", field: "acciones" },
    ];

    const filteredData = fetchedDetails.filter((det) => {
      const searchLower = searchQuery.toLowerCase();
      const detailMatches =
        det.scantilon_location.toLowerCase().includes(searchLower) ||
        det.name_detail.toLowerCase().includes(searchLower) ||
        det.material.toLowerCase().includes(searchLower) ||
        det.layer_thickness.toString().includes(searchLower);

      if (inModal) {
        if (tabStep4 === "muros") {
          return (
            detailMatches && det.scantilon_location.toLowerCase() === "muro"
          );
        } else if (tabStep4 === "techumbre") {
          return (
            detailMatches && det.scantilon_location.toLowerCase() === "techo"
          );
        } else if (tabStep4 === "pisos") {
          return (
            detailMatches && det.scantilon_location.toLowerCase() === "piso"
          );
        }
      }
      return detailMatches;
    });

    const data = filteredData.map((det) => {
      const isEditing = editingRowId === det.id_detail;
      return {
        scantilon_location: (
          <span
            style={{
              color: det.created_status !== "default" ? primaryColor : "black",
            }}
          >
            {det.scantilon_location}
          </span>
        ),
        name_detail: isEditing ? (
          <input
            type="text"
            className="form-control"
            value={editValues.name_detail || det.name_detail}
            onChange={(e) =>
              setEditValues((prev: any) => ({
                ...prev,
                name_detail: e.target.value,
              }))
            }
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <span
            style={{
              color: det.created_status !== "default" ? primaryColor : "black",
            }}
          >
            {det.name_detail}
          </span>
        ),
        material: (
          <span
            style={{
              color: det.created_status !== "default" ? primaryColor : "black",
            }}
          >
            {det.material}
          </span>
        ),
        layer_thickness: (
          <span
            style={{
              color: det.created_status !== "default" ? primaryColor : "black",
            }}
          >
            {det.layer_thickness}
          </span>
        ),
        acciones: (
          <>
            <CustomButton
              variant="layersIcon"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedItem({
                  id: det.id_detail,
                  name_detail: det.name_detail,
                });
                setShowDetailsModal(true);
              }}
            >
              <span className="material-symbols-outlined">stacks</span>
            </CustomButton>
            <CustomButton
              variant="editIcon"
              onClick={(e) => handleEditDetail(det, e)}
            >
              Editar
            </CustomButton>
            <CustomButton
              variant="deleteIcon"
              onClick={(e) => {
                e.stopPropagation();
                setShowDetailsModal(false);
                setDeletingDetail(det);
                setShowDeleteModal(true);
              }}
            >
              Eliminar
            </CustomButton>
          </>
        ),
      };
    });

    return (
      <>
        {!inModal && (
          <SearchParameters
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Buscar..."
            onNew={() => { }}
            newButtonText="Nuevo"
            style={{ marginBottom: "1rem" }}
          />
        )}
        <div className="custom-table-container">
          <TablesParameters columns={columnsDetails} data={data} />
        </div>
        {!inModal && (
          <div>
            <CustomButton
              variant="save"
              onClick={(e) => {
                e.stopPropagation();
                if (inModal) setShowDetailsModal(false);
                else setShowTabsInStep4(false);
              }}
            >
              <span className="material-icons">arrow_back</span> Volver
            </CustomButton>
          </div>
        )}
      </>
    );
  };

  const renderDetailsTabs = () => (
    <div>
      {/* Encabezado con buscador + botón Nuevo */}
      <div
        style={{
          display: "flex",
          gap: "1rem",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1rem",
          flexWrap: "wrap",
        }}
      >
        {/* Buscador */}
        <div style={{ flex: 1, minWidth: "200px" }}>
          <SearchParameters
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder={`Buscar ${tabStep4}`}
            onNew={() => { }}
            // si quieres inhabilitar el botón interno del componente:
            showNewButton={false}
          />
        </div>

        {/* Botón + Nuevo */}
        <NewDetailCreator
          detailType={
            tabStep4 === "muros"
              ? "Muro"
              : tabStep4 === "techumbre"
                ? "Techo"
                : "Piso"
          }
          onDetailCreated={refreshDetails}
        />      </div>

      {/* Tabs */}
      <HorizontalTabs
        tabs={[
          { key: "muros", label: "Muros" },
          { key: "techumbre", label: "Techumbre" },
          { key: "pisos", label: "Pisos" },
        ]}
        currentTab={tabStep4}
        onTabChange={(tab) => setTabStep4(tab as TabStep4)}
      />

      {/* Contenido de la tab seleccionada */}
      <div>
        {tabStep4 === "muros" && (
          <div onClick={() => setShowDetailsModal(true)}>
            {renderMurosTable()}
          </div>
        )}
        {tabStep4 === "techumbre" && (
          <div onClick={() => setShowDetailsModal(true)}>
            {renderTechumbreTable()}
          </div>
        )}
        {tabStep4 === "pisos" && (
          <div onClick={() => setShowDetailsModal(true)}>
            {renderPisosTable()}
          </div>
        )}
      </div>
    </div>
  );

  const renderMurosTable = () => {
    const columnsMuros = [
      {
        headerName: "Código IFC",
        field: "code_ifc",
      },
      { headerName: "Nombre Abreviado", field: "nombreAbreviado" },
      { headerName: "Valor U (W/m²K)", field: "valorU" },
      { headerName: "Color Exterior", field: "colorExterior" },
      { headerName: "Color Interior", field: "colorInterior" },
      { headerName: "Acciones", field: "acciones" },
    ];

    const data = searchFilter(murosTabList).map((item) => {
      const isEditing = editingRowId === (item.id_detail ?? item.id);
      return {
        code_ifc: item.code_ifc || "-",
        nombreAbreviado: isEditing ? (
          <input
            type="text"
            className="form-control form-control-sm"
            value={editValues.name_detail ?? ""}
            onClick={(e) => e.stopPropagation()}
            onChange={(e) =>
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                name_detail: e.target.value,
              }))
            }
          />
        ) : (
          item.name_detail
        ),
        valorU:
          item.value_u && Number(item.value_u) !== 0
            ? Number(item.value_u).toFixed(2)
            : "-",
        colorExterior: isEditing ? (
          <select
            onClick={(e) => e.stopPropagation()}
            value={
              editValues.exterior ||
              item.info?.surface_color?.exterior?.name ||
              ""
            }
            onChange={(e) =>
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                exterior: e.target.value,
              }))
            }
          >
            <option value="Claro">Claro</option>
            <option value="Oscuro">Oscuro</option>
            <option value="Intermedio">Intermedio</option>
          </select>
        ) : (
          item.info?.surface_color?.exterior?.name || "Desconocido"
        ),
        colorInterior: isEditing ? (
          <select
            onClick={(e) => e.stopPropagation()}
            value={
              editValues.interior ||
              item.info?.surface_color?.interior?.name ||
              ""
            }
            onChange={(e) =>
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                interior: e.target.value,
              }))
            }
          >
            <option value="Claro">Claro</option>
            <option value="Oscuro">Oscuro</option>
            <option value="Intermedio">Intermedio</option>
          </select>
        ) : (
          item.info?.surface_color?.interior?.name || "Desconocido"
        ),
        acciones: isEditing ? (
          <div onClick={(e) => e.stopPropagation()}>
            <ActionButtonsConfirm
              onAccept={() => handleInlineSave(item, "Muro")}
              onCancel={handleInlineCancel}
            />
          </div>
        ) : (
          <>
            <CustomButton
              variant="layersIcon"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedItem({
                  id: item.id_detail ?? item.id ?? 0,
                  name_detail: item.name_detail,
                });
                setShowDetailsModal(true);
              }}
            >
              <span className="material-symbols-outlined">stacks</span>
            </CustomButton>
            <CustomButton
              className="btn-table"
              variant="editIcon"
              onClick={(e) => {
                e.stopPropagation();
                handleInlineEdit(item, e);
              }}
            >
              Editar
            </CustomButton>
            <CustomButton
              className="btn-table"
              variant="deleteIcon"
              onClick={(e) => {
                e.stopPropagation();
                handleInlineDeleteModal(item, e);
              }}
            >
              Eliminar
            </CustomButton>
          </>
        ),
      };
    });

    return (
      <div>
        {murosTabList.length > 0 ? (
          <TablesParameters columns={columnsMuros} data={data} />
        ) : (
          <p>No hay datos</p>
        )}
      </div>
    );
  };

  const renderTechumbreTable = () => {
    const columnsTech = [
      {
        headerName: "Código IFC",
        field: "code_ifc",
      },
      { headerName: "Nombre Abreviado", field: "nombreAbreviado" },
      { headerName: "Valor U (W/m²K)", field: "valorU" },
      { headerName: "Color Exterior", field: "colorExterior" },
      { headerName: "Color Interior", field: "colorInterior" },
      { headerName: "Acciones", field: "acciones" },
    ];

    const data = searchFilter(techumbreTabList).map((item) => {
      const isEditing = editingRowId === (item.id_detail ?? item.id);
      return {
        code_ifc: item.code_ifc || "-",

        nombreAbreviado: isEditing ? (
          <input
            type="text"
            className="form-control form-control-sm"
            value={editValues.name_detail || item.name_detail}
            onClick={(e) => e.stopPropagation()}
            onChange={(e) =>
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                name_detail: e.target.value,
              }))
            }
          />
        ) : (
          item.name_detail
        ),
        valorU: item.value_u ? item.value_u.toFixed(2) : "-",
        colorExterior: isEditing ? (
          <select
            onClick={(e) => e.stopPropagation()}
            value={
              editValues.exterior ||
              item.info?.surface_color?.exterior?.name ||
              ""
            }
            onChange={(e) =>
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                exterior: e.target.value,
              }))
            }
          >
            <option value="Claro">Claro</option>
            <option value="Oscuro">Oscuro</option>
            <option value="Intermedio">Intermedio</option>
          </select>
        ) : (
          item.info?.surface_color?.exterior?.name || "Desconocido"
        ),
        colorInterior: isEditing ? (
          <select
            onClick={(e) => e.stopPropagation()}
            value={
              editValues.interior ||
              item.info?.surface_color?.interior?.name ||
              ""
            }
            onChange={(e) =>
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                interior: e.target.value,
              }))
            }
          >
            <option value="Claro">Claro</option>
            <option value="Oscuro">Oscuro</option>
            <option value="Intermedio">Intermedio</option>
          </select>
        ) : (
          item.info?.surface_color?.interior?.name || "Desconocido"
        ),
        acciones: isEditing ? (
          <div onClick={(e) => e.stopPropagation()}>
            <ActionButtonsConfirm
              onAccept={() => handleInlineSave(item, "Techo")}
              onCancel={handleInlineCancel}
            />
          </div>
        ) : (
          <>
            <CustomButton
              variant="layersIcon"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedItem({
                  id: item.id_detail ?? item.id ?? 0,
                  name_detail: item.name_detail,
                });
                setShowDetailsModal(true);
              }}
            >
              <span className="material-symbols-outlined">stacks</span>
            </CustomButton>
            <CustomButton
              variant="editIcon"
              className="btn-table"
              onClick={(e) => {
                e.stopPropagation();
                handleInlineEdit(item, e);
              }}
            >
              Editar
            </CustomButton>
            <CustomButton
              className="btn-table"
              variant="deleteIcon"
              onClick={(e) => {
                e.stopPropagation();
                handleInlineDeleteModal(item, e);
              }}
            >
              Eliminar
            </CustomButton>
          </>
        ),
      };
    });

    return (
      <div>
        {techumbreTabList.length > 0 ? (
          <TablesParameters columns={columnsTech} data={data} />
        ) : (
          <p>No hay datos</p>
        )}
      </div>
    );
  };

  const renderPisosTable = () => {
    const columnsPisos = [
      {
        headerName: "Código IFC",
        field: "code_ifc",
      },
      { headerName: "Nombre", field: "nombre" },
      { headerName: "U [W/m²K]", field: "uValue" },
      { headerName: "I [W/mK] (bajo piso)", field: "bajoPisoLambda" },
      { headerName: "e Aisl [cm] (bajo piso)", field: "bajoPisoEAisl" },
      { headerName: "I [W/mK] (vert)", field: "vertLambda" },
      { headerName: "e Aisl [cm] (vert)", field: "vertEAisl" },
      { headerName: "D [cm] (vert)", field: "vertD" },
      { headerName: "I [W/mK] (horiz)", field: "horizLambda" },
      { headerName: "e Aisl [cm] (horiz)", field: "horizEAisl" },
      { headerName: "D [cm] (horiz)", field: "horizD" },
      { headerName: "Acciones", field: "acciones" },
    ];

    const data = searchFilter(pisosTabList).map((item) => {
      const isEditing = editingRowId === (item.id_detail ?? item.id);
      const bajoPiso = item.info?.aislacion_bajo_piso || {};
      const vert = item.info?.ref_aisl_vertical || {};
      const horiz = item.info?.ref_aisl_horizontal || {};
      return {
        code_ifc: item.code_ifc || "-",

        nombre: isEditing ? (
          <input
            type="text"
            className="form-control form-control-sm"
            value={editValues.name_detail ?? ""}
            onClick={(e) => e.stopPropagation()}
            onChange={(e) =>
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                name_detail: e.target.value,
              }))
            }
          />
        ) : (
          item.name_detail
        ),
        uValue:
          item.value_u && Number(item.value_u) !== 0
            ? Number(item.value_u).toFixed(2)
            : "-",
        bajoPisoLambda:
          item.info?.aislacion_bajo_piso?.lambda &&
            Number(item.info.aislacion_bajo_piso.lambda) !== 0
            ? Number(item.info.aislacion_bajo_piso.lambda).toFixed(2)
            : "-",
        bajoPisoEAisl:
          item.info?.aislacion_bajo_piso?.e_aisl &&
            Number(item.info.aislacion_bajo_piso.e_aisl) !== 0
            ? Number(item.info.aislacion_bajo_piso.e_aisl).toFixed(2)
            : "-",
        vertLambda: isEditing ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={
              editValues.vertLambda !== undefined
                ? editValues.vertLambda
                : vert.lambda && Number(vert.lambda) !== 0
                  ? Number(vert.lambda).toFixed(2)
                  : ""
            }
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => {
              const value = e.target.value;
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                vertLambda: value === "0" ? "" : value,
              }));
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : vert.lambda && Number(vert.lambda) !== 0 ? (
          Number(vert.lambda).toFixed(2)
        ) : (
          "-"
        ),
        vertEAisl: isEditing ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={
              editValues.vertEAisl !== undefined
                ? editValues.vertEAisl
                : vert.e_aisl && Number(vert.e_aisl) !== 0
                  ? Number(vert.e_aisl).toFixed(2)
                  : ""
            }
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => {
              const value = e.target.value;
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                vertEAisl: value === "0" ? "" : value,
              }));
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : vert.e_aisl && Number(vert.e_aisl) !== 0 ? (
          Number(vert.e_aisl).toFixed(2)
        ) : (
          "-"
        ),
        vertD: isEditing ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={
              editValues.vertD !== undefined
                ? editValues.vertD
                : vert.d && Number(vert.d) !== 0
                  ? Number(vert.d).toFixed(2)
                  : ""
            }
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => {
              const value = e.target.value;
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                vertD: value === "0" ? "" : value,
              }));
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : vert.d && Number(vert.d) !== 0 ? (
          Number(vert.d).toFixed(2)
        ) : (
          "-"
        ),
        horizLambda: isEditing ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={
              editValues.horizLambda !== undefined
                ? editValues.horizLambda
                : horiz.lambda && Number(horiz.lambda) !== 0
                  ? Number(horiz.lambda).toFixed(2)
                  : ""
            }
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => {
              const value = e.target.value;
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                horizLambda: value === "0" ? "" : value,
              }));
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : horiz.lambda && Number(horiz.lambda) !== 0 ? (
          Number(horiz.lambda).toFixed(2)
        ) : (
          "-"
        ),
        horizEAisl: isEditing ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={
              editValues.horizEAisl !== undefined
                ? editValues.horizEAisl
                : horiz.e_aisl && Number(horiz.e_aisl) !== 0
                  ? Number(horiz.e_aisl).toFixed(2)
                  : ""
            }
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => {
              const value = e.target.value;
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                horizEAisl: value === "0" ? "" : value,
              }));
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : horiz.e_aisl && Number(horiz.e_aisl) !== 0 ? (
          Number(horiz.e_aisl).toFixed(2)
        ) : (
          "-"
        ),
        horizD: isEditing ? (
          <input
            type="number"
            min="0"
            className="form-control form-control-sm"
            value={
              editValues.horizD !== undefined
                ? editValues.horizD
                : horiz.d && Number(horiz.d) !== 0
                  ? Number(horiz.d).toFixed(2)
                  : ""
            }
            onClick={(e) => e.stopPropagation()}
            onChange={(e) => {
              const value = e.target.value;
              setEditValues((prev: Record<string, any>) => ({
                ...prev,
                horizD: value === "0" ? "" : value,
              }));
            }}
            onKeyDown={(e) => {
              if (e.key === "-") e.preventDefault();
            }}
          />
        ) : horiz.d && Number(horiz.d) !== 0 ? (
          Number(horiz.d).toFixed(2)
        ) : (
          "-"
        ),
        acciones: isEditing ? (
          <div onClick={(e) => e.stopPropagation()}>
            <ActionButtonsConfirm
              onAccept={() => handleInlineSave(item, "Piso")}
              onCancel={handleInlineCancel}
            />
          </div>
        ) : (
          <div style={{ width: "160px" }}>
            <CustomButton
              variant="layersIcon"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedItem({
                  id: item.id_detail ?? item.id ?? 0,
                  name_detail: item.name_detail,
                });
                setShowDetailsModal(true);
              }}
            >
              <span className="material-symbols-outlined">stacks</span>
            </CustomButton>
            <CustomButton
              className="btn-table"
              variant="editIcon"
              onClick={(e) => {
                e.stopPropagation();
                handleInlineEdit(item, e);
              }}
            >
              Editar
            </CustomButton>
            <CustomButton
              variant="deleteIcon"
              onClick={(e) => {
                e.stopPropagation();
                handleInlineDeleteModal(item, e);
              }}
            >
              Eliminar
            </CustomButton>
          </div>
        ),
      };
    });

    return (
      <div>
        {pisosTabList.length > 0 ? (
          <TablesParameters
            columns={columnsPisos}
            data={data}
            multiHeader={{
              rows: [
                // Fila 1: IFC, Nombre, U, grupos, Acciones
                [
                  { label: "Código IFC", field: "code_ifc", rowSpan: 2, sortable: true },
                  { label: "Nombre", field: "nombre", rowSpan: 2, sortable: true },
                  { label: "U [W/m²K]", field: "uValue", rowSpan: 2, sortable: true },
                  { label: "Aislamiento bajo piso", colSpan: 2 },
                  { label: "Ref Aisl Vert.", colSpan: 3 },
                  { label: "Ref Aisl Horiz.", colSpan: 3 },
                  { label: "Acciones", field: "acciones", rowSpan: 2, sortable: false },
                ],
                // Fila 2: las sub-columnas dentro de cada grupo
                [
                  { label: "λ [W/mK]", field: "bajoPisoLambda", sortable: true },
                  { label: "e Aisl [cm]", field: "bajoPisoEAisl", sortable: true },
                  { label: "λ [W/mK]", field: "vertLambda", sortable: true },
                  { label: "e Aisl [cm]", field: "vertEAisl", sortable: true },
                  { label: "D [cm]", field: "vertD", sortable: true },
                  { label: "λ [W/mK]", field: "horizLambda", sortable: true },
                  { label: "e Aisl [cm]", field: "horizEAisl", sortable: true },
                  { label: "D [cm]", field: "horizD", sortable: true },
                ],
              ],
            }}
          />


        ) : (
          <p>No hay datos</p>
        )}
      </div>
    );
  };

  return (
    <div className="constructive-details-container" style={{ padding: "20px" }}>
      <div style={{ marginTop: "20px" }}>
        {showTabsInStep4 ? renderDetailsTabs() : renderInitialDetails()}
      </div>

      <ModalCreate
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setDeletingDetail(null);
        }}
        onSave={() => {
          confirmDeleteDetail();
        }}
        title="Confirmar Eliminación"
        saveLabel="Eliminar"
        detail={deletingDetail}
      >
        <p>
          ¿Estás seguro que deseas eliminar el detalle{" "}
          <strong>{deletingDetail?.name_detail}</strong>?
        </p>
      </ModalCreate>

      <ModalCreate
        isOpen={showInlineDeleteModal}
        onClose={() => {
          setShowInlineDeleteModal(false);
          setDeletingInlineDetail(null);
        }}
        onSave={() => {
          confirmInlineDeleteDetail();
        }}
        title="Confirmar Eliminación"
        saveLabel="Eliminar"
        detail={deletingInlineDetail}
      >
        <p>
          ¿Estás seguro que deseas eliminar el detalle{" "}
          <strong>{deletingInlineDetail?.name_detail}</strong>?
        </p>
      </ModalCreate>

      {editingDetail && (
        <ModalCreate
          isOpen={true}
          title="Editar Detalle"
          detail={editingDetail}
          onClose={() => {
            setEditingDetail(null);
          }}
          onSave={() => {
            handleConfirmEditDetail({
              stopPropagation: () => { },
              preventDefault: () => { },
              nativeEvent: new MouseEvent("click"),
              isDefaultPrevented: () => false,
              isPropagationStopped: () => false,
              persist: () => { },
              target: document.createElement("button"),
              currentTarget: document.createElement("button"),
              bubbles: true,
              cancelable: true,
              defaultPrevented: false,
              eventPhase: 0,
              isTrusted: true,
              altKey: false,
              button: 0,
              buttons: 0,
              clientX: 0,
              clientY: 0,
              ctrlKey: false,
              metaKey: false,
              movementX: 0,
              movementY: 0,
              pageX: 0,
              pageY: 0,
              relatedTarget: null,
              screenX: 0,
              screenY: 0,
              shiftKey: false,
              type: "click",
              x: 0,
              y: 0,
            } as unknown as React.MouseEvent<Element, MouseEvent>);
          }}
        >
          <form>
            <div className="form-group">
              <label>Ubicación Detalle</label>
              <input
                type="text"
                className="form-control"
                value={editingDetail.scantilon_location}
                readOnly
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            <div className="form-group">
              <label>Nombre Detalle</label>
              <input
                type="text"
                className="form-control"
                value={editingDetail.name_detail}
                onChange={(e) =>
                  setEditingDetail((prev) =>
                    prev ? { ...prev, name_detail: e.target.value } : prev
                  )
                }
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            <div className="form-group">
              <label>Material</label>
              <select
                className="form-control"
                value={
                  editingDetail.material_id
                    ? editingDetail.material_id.toString()
                    : ""
                }
                onChange={(e) =>
                  setEditingDetail((prev) =>
                    prev
                      ? { ...prev, material_id: Number(e.target.value) }
                      : prev
                  )
                }
                onClick={(e) => {
                  e.stopPropagation();
                  fetchMaterials();
                }}
              >
                <option value="">Seleccione Material</option>
                {materials.map((mat) => (
                  <option key={mat.id} value={mat.id.toString()}>
                    {mat.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Espesor de capa (cm)</label>
              <input
                type="number"
                min="1"
                className="form-control"
                value={editingDetail.layer_thickness}
                onChange={(e) =>
                  setEditingDetail((prev) =>
                    prev
                      ? { ...prev, layer_thickness: Number(e.target.value) }
                      : prev
                  )
                }
                onClick={(e) => e.stopPropagation()}
                onKeyDown={(e) => {
                  if (e.key === "-") e.preventDefault();
                }}
              />
            </div>
          </form>
        </ModalCreate>
      )}

      {showDetailsModal && selectedItem && (
        <DetailModal
          isOpen={showDetailsModal}
          onClose={() => {
            setShowDetailsModal(false);
            refreshDetails();
          }}
          selectedItem={selectedItem}
          refreshParent={refreshDetails}
          materials={materials}
          fetchMaterials={fetchMaterials}
        />
      )}
    </div>
  );
};

export default ConstructiveDetailsComponent;
