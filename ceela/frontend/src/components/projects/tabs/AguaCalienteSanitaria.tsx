import { useApi } from "@/hooks/useApi";
import { useConstants } from "@/hooks/useConstantsHook";
import { notify } from "@/utils/notify";
import { Plus, Save, Trash2 } from "lucide-react"; // Importing Lucide icons
import { useEffect, useState } from "react";
import { Card, Col, Form, Row, Table } from "react-bootstrap";
import CustomButton from "../../common/CustomButton"; // Assuming CustomButton is located here


interface AguaCalienteSanitariaProps {
  onlyView?: boolean;
  onSaveSuccess?: () => void;
  actualizarStatus?: () => void;
}

const AguaCalienteSanitaria: React.FC<AguaCalienteSanitariaProps> = ({
  onlyView = false,
  onSaveSuccess,
  actualizarStatus,
}) => {
  const result = useConstants("energy_systems", "general");
  const occupancyResult = useConstants("acs", "occupancy");
  const tempRedResult = useConstants("temperature", "red");
  const waterMonthly = useConstants("water", "monthly");

  const acsDataList = Object.entries(
    occupancyResult.constant?.atributs?.tipo_de_ocupacion_acs || {}
  ).map(([tipo, consumo]) => ({ tipo, cantidad: 0, consumo: Number(consumo) }));

  interface TableRow {
    tipo: string;
    cantidad: number;
    consumo: number;
  }

  const [tableData, setTableData] = useState<TableRow[]>([]);
  const [demandaACS, setDemandaACS] = useState<number>(100);
  const [consumoACS, setConsumoACS] = useState<number>(3.251);
  const [consumoEnergiaPrimariaACS, setConsumoEnergiaPrimariaACS] =
    useState<number>(3.576);
  const [co2eqEnergiaPrimaria, setCo2eqEnergiaPrimaria] = useState<number>(815);
  const [combustible, setCombustible] = useState<any>("");
  const [rendimiento, setRendimiento] = useState<string>("");
  const [sistDistribucion, setSistDistribucion] = useState<string>("");
  const [sistControl, setSistControl] = useState<string | number>(
    "Automático base a T° agua"
  );
  const [tAcs, setTAcs] = useState<number>(0);

  const [combustibleOptions, setCombustibleOptions] = useState<
    { value: string; label: string; fep: number }[]
  >([]);
  const [rendimientoOptions, setRendimientoOptions] = useState<
    { value: string; label: string; rendimiento: number }[]
  >([]);
  const [sistDistribucionOptions, setSistDistribucionOptions] = useState<
    { value: string; label: string; distribucion: number }[]
  >([]);
  const [sistControlOptions, setSistControlOptions] = useState<
    { value: string; label: string; control: number }[]
  >([]);

  const [energySourceConsumption, setEnergySourceConsumption] = useState<{
    [key: string]: number;
  }>({});
  useEffect(() => {
    if (result.constant?.atributs?.consumos_por_fuente_de_energia) {
      setEnergySourceConsumption(
        result.constant?.atributs?.consumos_por_fuente_de_energia
      );
    }
  }, []);
  const api = useApi()

  useEffect(() => {
    const fetchExistingData = async () => {
      try {
        const pathname = window.location.pathname;
        const projectId = pathname.includes("workflow-part2-create")
          ? localStorage.getItem("last_created_project")
          : localStorage.getItem("project_id");

        if (!projectId) {
          notify("No se encontró el ID del proyecto");
          return;
        }

        const response = await api.get(
          `/agua-caliente-obtener/${projectId}`,
        );

        const data = response[0];
        if (data) {
          setTAcs(data.t_acs);
          setDemandaACS(data.demanda_acs);
          setCombustible(data.combustible);
          setRendimiento(data.rendimiento);
          setSistDistribucion(data.sist_distribucion);
          setSistControl(data.sis_control);
          setConsumoACS(data.consumo_acs);
          setConsumoEnergiaPrimariaACS(data.consumo_energia_primaria);
          setCo2eqEnergiaPrimaria(data.energia_primaria);
          console.log("Data fetched:", data.data);
          // Transform and set table data
          const transformedData = data?.data.map((item: any) => ({
            tipo: item.tipo_ocupacion,
            cantidad: item.cantidad_personas,
            consumo: item.pers_dia,
          }));
          setTableData(transformedData);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        // notify("Error al obtener los datos");
      }
    };

    fetchExistingData();
  }, []); // Run once when component mounts

  useEffect(() => {
    const daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    // Calculate total daily consumption from table data
    const sumTotalConsumo = tableData.reduce(
      (acc, row) => acc + row.cantidad * row.consumo,
      0
    );

    // Calculate monthly consumption (liters per month)
    const litrosMes = daysInMonth.map((days) => sumTotalConsumo * days);

    console.log("Total consumo diario:", sumTotalConsumo);
    console.log("Litros por mes:", litrosMes);
    tempRedResult.constant?.atributs?.monthly;
    const monthlyTemp = Object.entries(
      tempRedResult.constant?.atributs?.monthly || {}
    )
      .sort((a, b) => {
        const months = [
          "january",
          "february",
          "march",
          "april",
          "may",
          "june",
          "july",
          "august",
          "september",
          "october",
          "november",
          "december",
        ];
        return months.indexOf(a[0]) - months.indexOf(b[0]);
      })
      .map(([_, value]) => (isNaN(Number(value)) ? 0 : Number(value)));

    console.log(monthlyTemp);
    const litrosDtMes = litrosMes.map((litros, index) => {
      const value = litros * (tAcs - Number(monthlyTemp[index]));
      return isNaN(value) ? 0 : value;
    });

    const sumLitrosDtmes = litrosDtMes.reduce((acc, value) => acc + value, 0);
    setDemandaACS(parseFloat((sumLitrosDtmes / 860).toFixed(2))); // Limitar a 2 decimales
  }, [tableData, tAcs]);

  const [combustibleLabel, setCombustibleLabel] = useState<string>("");

  useEffect(() => {
    if (result.constant?.atributs) {
      const { combustibles, rendimiento_acs, distribucion_acs, control_acs } =
        result.constant.atributs;

      setCombustibleOptions(
        combustibles.map((item: any) => ({
          value: item.code,
          label: item.name,
          fep: item.fep,
        }))
      );
      setRendimientoOptions(
        rendimiento_acs.map((item: any) => ({
          value: item.code,
          label: item.name,
          rendimiento: item.value,
        }))
      );
      setSistDistribucionOptions(
        distribucion_acs.map((item: any) => ({
          value: item.code,
          label: item.name,
          distribucion: item.value,
        }))
      );
      setSistControlOptions(
        control_acs.map((item: any) => ({
          value: item.code,
          label: item.name,
          control: item.value,
        }))
      );

      // Set default values only if they are not already set
      if (!combustible && combustibles.length > 0)
        setCombustible(combustibles[0].code);
      if (!rendimiento && rendimiento_acs.length > 0)
        setRendimiento(rendimiento_acs[0].code);
      if (!sistDistribucion && distribucion_acs.length > 0)
        setSistDistribucion(distribucion_acs[0].code);
      if (!sistControl && control_acs.length > 0)
        setSistControl(control_acs[0].code);
    }
  }, [result.constant]);

  const getValueFromValue = (options: any[], code: string, key: string) => {
    const option = options.find((opt) => opt.value === code);
    return option ? option[key] : 1;
  };

  const getValueFromCode = (options: any[], name: string, key: string) => {
    const option = options.find((opt) => opt?.code === name);
    return option?.[key];
  };

  useEffect(() => {
    const rendimientoValue = getValueFromValue(
      rendimientoOptions,
      rendimiento,
      "rendimiento"
    );
    const sistDistribucionValue = getValueFromValue(
      sistDistribucionOptions,
      sistDistribucion,
      "distribucion"
    );
    const sistControlValue = getValueFromValue(
      sistControlOptions,
      sistControl as string,
      "control"
    );

    if (rendimientoValue && sistDistribucionValue && sistControlValue) {
      const calculatedConsumoACS =
        demandaACS /
        (rendimientoValue * sistDistribucionValue * sistControlValue);
      setConsumoACS(parseFloat(calculatedConsumoACS.toFixed(3)));
    }
  }, [
    demandaACS,
    rendimiento,
    sistDistribucion,
    sistControl,
    rendimientoOptions,
    sistDistribucionOptions,
    sistControlOptions,
  ]);
 
  useEffect(() => {
    const rendimientoValue = getValueFromValue(
      rendimientoOptions,
      rendimiento,
      "rendimiento"
    );
    const sistDistribucionValue = getValueFromValue(
      sistDistribucionOptions,
      sistDistribucion,
      "distribucion"
    );
    const sistControlValue = getValueFromValue(
      sistControlOptions,
      String(sistControl),
      "control"
    );
    const combustibleFep = getValueFromValue(
      combustibleOptions,
      combustible,
      "fep"
    );

    if (
      rendimientoValue &&
      sistDistribucionValue &&
      sistControlValue &&
      combustibleFep
    ) {
      const calculatedConsumoEnergiaPrimariaACS =
        (combustibleFep * demandaACS) /
        (sistControlValue * sistDistribucionValue * rendimientoValue);
      setConsumoEnergiaPrimariaACS(
        parseFloat(calculatedConsumoEnergiaPrimariaACS.toFixed(3))
      );
    }

    const co2EqValue = getValueFromCode(
      result.constant?.atributs?.consumos_por_fuente_de_energia || [],
      combustible,
      "co2_eq"
    );

    if (co2EqValue && consumoEnergiaPrimariaACS) {
      const calculatedCo2Eq = co2EqValue * consumoEnergiaPrimariaACS;
      setCo2eqEnergiaPrimaria(parseFloat(calculatedCo2Eq.toFixed(3)));
    }
  }, [
    demandaACS,
    rendimiento,
    sistDistribucion,
    sistControl,
    combustible,
    consumoEnergiaPrimariaACS,
    rendimientoOptions,
    sistDistribucionOptions,
    sistControlOptions,
    combustibleOptions,
    result.constant?.atributs?.consumos_por_fuente_de_energia,
  ]);

  const handleInputChange = (
    index: number,
    field: keyof TableRow,
    value: string
  ) => {
    const updatedData = [...tableData];
    if (field === "tipo") {
      const selectedOption = acsDataList.find(
        (option) => option.tipo === value
      );
      updatedData[index].consumo = selectedOption ? selectedOption.consumo : 0;
    }
    updatedData[index] = {
      ...updatedData[index],
      [field]:
        field === "cantidad" || field === "consumo"
          ? parseFloat(value) || 0
          : value,
    };
    setTableData(updatedData);
  };

  const addRow = () => {
    const newRow =
      acsDataList.length > 0
        ? acsDataList[0]
        : { tipo: "", cantidad: 0, consumo: 0 };
    setTableData([...tableData, { ...newRow }]);
  };

  const deleteRow = (index: number) => {
    const updatedData = tableData.filter((_, i) => i !== index);
    setTableData(updatedData);
  };

  const handleCombustibleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedCode = e.target.value;
    const selectedOption = combustibleOptions.find(
      (option) => option.value === selectedCode
    );
    if (selectedOption) {
      setCombustible(selectedOption.value);
      setCombustibleLabel(selectedOption.label);
    }
  };

  const saveData = async () => {
    try {
      const pathname = window.location.pathname;
      const projectId = pathname.includes("workflow-part2-create")
        ? localStorage.getItem("last_created_project")
        : localStorage.getItem("project_id");

      if (!projectId) {
        notify("No se encontró el ID del proyecto");
        return;
      }

      const requestData = {
        t_acs: tAcs,
        demanda_acs: demandaACS,
        combustible: combustible,
        rendimiento: rendimiento,
        sist_distribucion: sistDistribucion,
        sis_control: sistControl,
        consumo_acs: consumoACS,
        consumo_energia_primaria: consumoEnergiaPrimariaACS,
        energia_primaria: co2eqEnergiaPrimaria,
        data: tableData.map((row) => ({
          tipo_ocupacion: row.tipo,
          cantidad_personas: row.cantidad,
          pers_dia: row.consumo,
        })),
      };

      const response = await api.post(
        `/agua-caliente/${projectId}`,
        requestData,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
            "Content-Type": "application/json",
          },
        }
      );

      notify("Datos guardados exitosamente");
      if (actualizarStatus) await actualizarStatus();
      if (onSaveSuccess) onSaveSuccess();
    } catch (error) {
      console.error("Error saving data:", error);
      notify("Error al guardar los datos");
    }
  };

  return (
    <Row className="mb-4">
      <Col md={12}>
        {/* <Card className="shadow"> */}
        {/* <Card.Body> */}
        {/* <Card.Title className="text-center text-dark"> */}
        {/* Agua Caliente Sanitaria */}
        {/* </Card.Title> */}
        <Card className="shadow col-10 mx-auto">
          <Card.Body>
            {!onlyView && (
              <div
                style={{
                  marginBottom: "15px",
                }}
              >
                <CustomButton
                  style={{ display: "block", marginLeft: "auto" }}
                  className="mt-3"
                  onClick={addRow}
                >
                  <Plus className="me-1" size={16} /> Nuevo
                </CustomButton>
              </div>
            )}
            <Table responsive className="table-sm mb-0">
              <thead className="">
                <tr>
                  <th style={{ textAlign: "center" }}>
                    Tipo de ocupación para sistema ACS
                  </th>
                  <th style={{ textAlign: "center" }}>Cantidad personas</th>
                  <th style={{ textAlign: "center" }}>
                    <span className="fw-bold">[l/pers]</span>
                  </th>
                  <th style={{ textAlign: "center" }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {tableData.map((row, index) => (
                  <tr key={index}>
                    <td>
                      <Form.Select
                        disabled={onlyView}
                        value={row.tipo}
                        onChange={(e) =>
                          handleInputChange(index, "tipo", e.target.value)
                        }
                      >
                        {acsDataList.map((option, i) => (
                          <option key={i} value={option.tipo}>
                            {option.tipo}
                          </option>
                        ))}
                      </Form.Select>
                    </td>
                    <td>
                      <Form.Control
                        disabled={onlyView}
                        type="number"
                        min="0"
                        value={row.cantidad}
                        onChange={(e) =>
                          handleInputChange(index, "cantidad", e.target.value)
                        }
                      />
                    </td>
                    <td style={{ textAlign: "center" }}>
                      {(row.cantidad * row.consumo).toFixed(2)}
                    </td>
                    <td style={{ textAlign: "center" }}>
                      {!onlyView && (
                        <CustomButton
                          variant="deleteIcon"
                          onClick={() => deleteRow(index)}
                        >
                          <Trash2 className="me-1" size={16} />
                        </CustomButton>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
        <Card className="shadow col-10 mx-auto">
          <Card.Body>
            <div className="mt-3">
              <Form.Group as={Row} className="align-items-center">
                <Form.Label column sm={4} className="text-end font-bold">
                  T&apos; ACS
                </Form.Label>
                <Col sm={4} className="text-end">
                  <Form.Control
                    disabled={onlyView}
                    type="number"
                    min="0"
                    value={tAcs}
                    onChange={(e) => setTAcs(parseFloat(e.target.value) || 0)}
                    style={{ color: "#2ab0c5", fontSize: "0.9rem" }}
                  />
                </Col>
                <Col sm={3} className="align-self-center text-start">
                  <span>°C</span>
                </Col>
              </Form.Group>
            </div>
            <div className="mt-3">
              <Form.Group as={Row} className="align-items-center">
                <Form.Label column sm={4} className="text-end">
                  Demanda ACS
                </Form.Label>
                <Col sm={4} className="text-end">
                  <div className="form-control-plaintext fw-bold">
                    {demandaACS}
                  </div>
                </Col>
                <Col sm={3} className="align-self-center text-start">
                  <span>[kWh]</span>
                </Col>
              </Form.Group>
            </div>

            <div className="mt-3">
              <Form.Group as={Row} className="align-items-center">
                <Form.Label column sm={4} className="text-end">
                  Combustible
                </Form.Label>
                <Col sm={3} className="text-end">
                  <Form.Select
                    disabled={onlyView}
                    value={combustible}
                    onChange={handleCombustibleChange}
                    style={{ color: "#2ab0c5", fontSize: "0.9rem" }}
                  >
                    <option value="">Seleccione</option>
                    {combustibleOptions.map((option, i) => (
                      <option key={i} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Col>
                <Col sm={1} className="align-self-center text-end">
                  <span>
                    <b>{getValueFromValue(combustibleOptions, combustible, "fep")}</b>
                  </span>
                </Col>
                <Col sm={1} className="align-self-center text-start">
                  <span></span>
                </Col>
              </Form.Group>
            </div>
            <div className="mt-3">
              <Form.Group as={Row} className="align-items-center">
                <Form.Label column sm={4} className="text-end">
                  Rendimiento
                </Form.Label>
                <Col sm={3} className="text-end">
                  <Form.Select
                    disabled={onlyView}
                    value={rendimiento}
                    onChange={(e) => setRendimiento(e.target.value)}
                    style={{ color: "#2ab0c5", fontSize: "0.9rem" }}
                  >
                    <option value="">Seleccione</option>
                    {rendimientoOptions.map((option, i) => (
                      <option key={i} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Col>
                <Col sm={1} className="align-self-center text-end">
                  <span>
                    <b>
                      {getValueFromValue(
                        rendimientoOptions,
                        rendimiento,
                        "rendimiento"
                      )}
                    </b>
                  </span>
                </Col>
                <Col sm={1} className="align-self-center text-start">
                  <span></span>
                </Col>
              </Form.Group>
            </div>
            <div className="mt-3">
              <Form.Group as={Row} className="align-items-center">
                <Form.Label column sm={4} className="text-end">
                  Sist. Distribución
                </Form.Label>
                <Col sm={3} className="text-end">
                  <Form.Select
                    disabled={onlyView}
                    value={sistDistribucion}
                    onChange={(e) =>
                      setSistDistribucion(String(e.target.value))
                    }
                    style={{ color: "#2ab0c5", fontSize: "0.9rem" }}
                  >
                    <option value="">Seleccione</option>
                    {sistDistribucionOptions.map((option, i) => (
                      <option key={i} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Col>
                <Col sm={1} className="align-self-center text-end">
                  <span>
                    <b>{getValueFromValue(
                      sistDistribucionOptions,
                      sistDistribucion,
                      "distribucion"
                    )}</b>
                  </span>
                </Col>
                <Col sm={1} className="align-self-center text-start">
                  <span></span>
                </Col>
              </Form.Group>
            </div>
            <div className="mt-3">
              <Form.Group as={Row} className="align-items-center">
                <Form.Label column sm={4} className="text-end">
                  Sist. Control
                </Form.Label>
                <Col sm={3} className="text-end">
                  <Form.Select
                    disabled={onlyView}
                    value={sistControl}
                    onChange={(e) => setSistControl(e.target.value)}
                    style={{ color: "#2ab0c5", fontSize: "0.9rem" }}
                  >
                    <option value="">Seleccione</option>
                    {sistControlOptions.map((option, i) => (
                      <option key={i} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Col>
                <Col sm={1  } className="align-self-center text-end">
                  <span>
                    <b>{getValueFromValue(
                      sistControlOptions,
                      String(sistControl),
                      "control"
                    )}</b>
                  </span>
                </Col>
                <Col sm={1} className="align-self-center text-start">
                   <span></span>
                </Col>
              </Form.Group>
            </div>
            <div className="mt-3">
              <Form.Group as={Row} className="align-items-center">
                <Form.Label column sm={4} className="text-end">
                  Consumo ACS
                </Form.Label>
                <Col sm={4} className="text-end">
                  <div className="form-control-plaintext fw-bold">
                    {consumoACS}
                  </div>
                </Col>
                <Col sm={3} className="align-self-center text-start">
                  <span>[kWh]</span>
                </Col>
              </Form.Group>
            </div>
            <div className="mt-3">
              <Form.Group as={Row} className="align-items-center">
                <Form.Label column sm={4} className="text-end">
                  Consumo Energía primaria ACS
                </Form.Label>
                <Col sm={4} className="text-end">
                  <div className="form-control-plaintext fw-bold">
                    {consumoEnergiaPrimariaACS}
                  </div>
                </Col>
                <Col sm={3} className="align-self-center text-start">
                  <span>[kWh]</span>
                </Col>
              </Form.Group>
            </div>
            <div className="mt-3">
              <Form.Group as={Row} className="align-items-center">
                <Form.Label column sm={4} className="text-end">
                  CO2eq Energía primaria
                </Form.Label>
                <Col sm={4} className="text-end">
                  <div className="form-control-plaintext fw-bold">
                    {co2eqEnergiaPrimaria}
                  </div>
                </Col>
                <Col sm={3} className="align-self-center text-start">
                  <span>[kg CO2]</span>
                </Col>
              </Form.Group>
            </div>
          </Card.Body>
        </Card>
        {!onlyView && (
          <CustomButton
            onClick={saveData}
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.2s ease-in-out",
              backgroundColor: "var(--primary-color)",
              border: "none",
              fontSize: "14px",
              borderRadius: "8px",
              padding: "10px 16px",
              cursor: "pointer",
              boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
              fontWeight: 500,
              letterSpacing: "0.3px",
              minWidth: "max-content",
              whiteSpace: "normal",
              lineHeight: 1.5,
              height: "auto",
              width: "100px",
              float: "right",
            }}
            color="orange"
            className="btn btn-sm mt-2 m-2 hover:opacity-80 transition-opacity duration-200"
          >
            <Save className="me-2" size={18} />
            Guardar Datos
          </CustomButton>
        )}
        {/* </Card.Body> */}
        {/* </Card> */}
      </Col>
    </Row>
  );
};


export default AguaCalienteSanitaria;

