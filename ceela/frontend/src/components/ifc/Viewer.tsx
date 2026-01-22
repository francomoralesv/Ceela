"use client";
import { useProjectIfcBuilder } from '@/hooks/ifc/useProjectIfcBuilder';
import { IFC_PROP, IFC_TYPES } from '@/constants/ifc';
import { getPropValue } from '@/lib/utils';
import { notify } from '@/utils/notify';
import "bootstrap/dist/css/bootstrap.min.css";
import { Check, Loader2 } from "lucide-react";
import { useRouter } from 'next/router';
import { useEffect, useState } from "react";
import { Col, Container, Row } from "react-bootstrap";
import Card from "../common/Card";
import CustomButton from "../common/CustomButton";
import IFCUploader from "./IfcUploader";
import { ErrorDetailsAccordion } from './components/ErrorDetailsAccordion';
import { MissingElementsPanel } from './components/MissingElementsPanel';
import { ProjectStatusPanel } from './components/ProjectStatusPanel';
import { orientationToAzimutRange } from '@/utils/azimut';
import { Room } from '@/shared/interfaces/ifc.interface';

/**
 * Dynamically loads the IFC viewer component
 */
const loadIFCViewer = async () => {
  const { default: IFCViewer } = await import("@bytestone/ifc-component");
  return IFCViewer;
};

/**
 * Main IFC viewer component
 */
export default function IFCViewerComponent() {
  // Component state
  const [viewerInstance, setViewerInstance] = useState<any>(null);
  const [objectsData, setObjectsData] = useState<Array<{
    id: string;
    metadata: any;
    name: string;
    parent: string;
    props: Array<object>;
    type: string;
  }>>([]);
  const [status, setStatus] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [fileSelected, setFileSelected] = useState<boolean>(false);
  const [missingElements, setMissingElements] = useState<Array<{ type: string; name: string }>>([]);
  const [isUploadComplete, setIsUploadComplete] = useState<boolean>(false);

  // Hooks
  const router = useRouter();
  const [projectId, setProjectId] = useState<string>('');
  const projectBuilder = useProjectIfcBuilder(projectId);

  // Event handlers and utility functions
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event;
    if (file) {
      setFileSelected(true);
      loadIFCViewer().then((IFCViewer) => {
        viewerInstance?.unloadModel();
        setViewerInstance(
          new IFCViewer({ canvasId: "myCanvas", modelPath: "/api/serve-xkt" })
        );
      });
    }
  };
  // Generate the structured output from objects
  const generateStructuredOutput = (objects: Array<any>): Room[] => {
    const rooms = objects.filter(obj => obj.type.includes(IFC_TYPES.IFCSpace));
    console.log(rooms);
    return rooms?.map(room => {
      const roomCode = getPropValue(room, IFC_PROP.ROOM_CODE, getPropValue(room, IFC_PROP.ROOM_NAME));
      if (!roomCode)
        throw new Error(IFC_PROP.ROOM_CODE_ERROR); // AU
      const roomEnclosureType = getPropValue(room, IFC_PROP.ROOM_TYPE, getPropValue(room, IFC_PROP.ROOM_NAME));
      if (!roomEnclosureType)
        throw new Error(IFC_PROP.ROOM_TYPE_ERROR); // AUDITORIO

      const wallCodes: string[] = [];
      room.props.forEach((prop: any) => {
        if (prop.name && prop.name.startsWith('M_') && prop.value) {
          wallCodes.push(prop.value);
        }
      });
      // Get all walls associated with this room
      const roomWalls = objects.filter(obj =>
        obj.type.includes(IFC_TYPES.IFCWall) &&
        (obj.props.some((p: any) => p.name === IFC_PROP.ASSIGNED_ROOM && p.value === roomEnclosureType) ||
         obj.props.some((p: any) => p.name === IFC_PROP.ASSIGNED_ROOM && p.value === roomCode) ||
         wallCodes.some(code => obj.props.some((p: any) => p.name === IFC_PROP.WALL_CODE && p.value === code))
        )
      );
      // Calculate average height from walls (using y dimension)
      let averageWallHeight = 0;
      if (roomWalls.length > 0) {
        const totalHeight = roomWalls.reduce((sum, wall) => {
          // Use wall.dimensions.y as the height if available
          return sum + (wall.dimensions?.y || 0);
        }, 0);
        averageWallHeight = totalHeight / roomWalls.length;
      }

      // Find floor codes associated with this room
      const floorCodes: string[] = [];
      room.props.forEach((prop: any) => {
        if ((prop.name === IFC_PROP.FLOOR_ROOM && prop.value)) {
          floorCodes.push(prop.value);
        }
      });

      const roomFloors = objects.filter(obj =>
        obj.type.includes(IFC_TYPES.IFCSLab) &&
        (obj.props.some((p: any) => p.name === IFC_PROP.ASSIGNED_ROOM && p.value === roomCode) ||
          floorCodes.some(code => obj.props.some((p: any) => p.name === IFC_PROP.WALL_CODE && p.value === code)))
      );
      const ceilingCodes: string[] = [];
      room.props.forEach((prop: any) => {
        if (prop.name === IFC_PROP.CEILING_ROOM && prop.value) {
          ceilingCodes.push(prop.value);
        }
      });
      // Find doors associated with this room
      const doors = objects.filter(obj =>
        obj.type.includes(IFC_TYPES.IFCDoor) &&
        obj.props.some((p: any) => p.name === IFC_PROP.ASSIGNED_ROOM && p.value === roomEnclosureType)
      );

      const name = getPropValue(room, IFC_PROP.ROOM_NAME);
      const roomType = getPropValue(room, IFC_PROP.ROOM_TYPE, name)

      if (!name)
        throw new Error(IFC_PROP.ROOM_NAME_ERROR);
      return {
        id: room.id,
        name,
        type: roomEnclosureType,
        properties: {
          roomCode: roomCode,
          roomType,
          occupationProfile: {
            code: roomCode, // CÓDIGO DE RECINTO
            type: roomType || IFC_PROP.UNKNOWN, // TIPOLOGÍA DE RESINTO
            occupation: getPropValue(room, IFC_PROP.ROOM_TYPE, name) || IFC_PROP.UNKNOWN
          },
          level: getPropValue(room, IFC_PROP.LEVEL, name) || IFC_PROP.UNKNOWN,
          volume: room.volume || getPropValue(room, IFC_PROP.VOLUME, name) || 0,
          surfaceArea: room.surfaceArea || 0,
          averageHeight: averageWallHeight > 0 ? averageWallHeight.toFixed(2) :
            (room.dimensions?.z ||
              (room.volume && room.surfaceArea ? room.volume / room.surfaceArea.toFixed(2) :
                getPropValue(room, IFC_PROP.HEIGHT, name) ||
                (getPropValue(room, IFC_PROP.VOLUME, name) && getPropValue(room, IFC_PROP.AREA, name) ?
                  (Number(getPropValue(room, IFC_PROP.VOLUME, name)) / Number(getPropValue(room, IFC_PROP.AREA, name))) :
                  IFC_PROP.UNKNOWN))),
          wallsAverageHeight: averageWallHeight > 0 ? averageWallHeight : 0,
          dimensions: room.dimensions || {
            x: 0,
            y: 0,
            z: 0
          },
          position: room.position || {
            x: 0,
            y: 0,
            z: 0
          }
        },
        constructionDetails: {
          walls: wallCodes.map(code => {
            const walls = objects.filter(obj =>
              obj.type.includes(IFC_TYPES.IFCWall) &&
              obj.props.some((p: any) => p.name === IFC_PROP.WALL_CODE && p.value === code)
            );
            const windows = objects.filter(obj =>
              obj.type.includes(IFC_TYPES.IFCWindow) &&
              obj.props.some((p: any) => p.name === IFC_PROP.ASSIGNED_WALL && p.value === code)
            );
            // Extract thermal bridges for this wall group
            const thermalBridges = walls.flatMap(wall => {
              const bridges = [];
              // Check for thermal bridge properties in wall
              const po1Length = getPropValue(wall, IFC_PROP.P01_L);
              const po1Element = getPropValue(wall, IFC_PROP.P01_ELEMENTO2);
              const po2Length = getPropValue(wall, IFC_PROP.P02_L);
              const po2Element = getPropValue(wall, IFC_PROP.P02_ELEMENTO2);
              const po3Length = getPropValue(wall, IFC_PROP.P03_L);
              const po3Element = getPropValue(wall, IFC_PROP.P03_ELEMENTO2);
              const po4Length = getPropValue(wall, IFC_PROP.P04_L);
              const po4Element = getPropValue(wall, IFC_PROP.P04_ELEMENTO2);
              const fav1 = getPropValue(wall, IFC_PROP.FAV1);
              const fav2 = getPropValue(wall, IFC_PROP.FAV2);
              const fav3 = getPropValue(wall, IFC_PROP.FAV3);
              
              if (po1Length || po1Element || po2Length || po2Element || po3Length || po3Element || po4Length || po4Element || fav1 || fav2 || fav3) {
                bridges.push({
                  po1_length: Number(po1Length) || 0,
                  po1_element: po1Element || '',
                  po2_length: Number(po2Length) || 0,
                  po2_element: po2Element || '',
                  po3_length: Number(po3Length) || 0,
                  po3_element: po3Element || '',
                  po4_length: Number(po4Length) || 0,
                  po4_e_aislacion: 0, // This would need additional IFC property if available
                  po4_element: po4Element || '',
                  fav1: Number(fav1) || 0,
                  fav2: Number(fav2) || 0,
                  fav3: Number(fav3) || 0,
                });
              }
              return bridges;
            });

            return {
              code: code,
              windows: windows?.map(window => {
                return {
                  id: window.id,
                  code: getPropValue(window, IFC_PROP.WINDOW_CODE, name, true),
                  name: window.name,
                  type: window.type,
                  width: window.dimensions?.x || getPropValue(window, IFC_PROP.WIDTH) || 0,
                  height: window.dimensions?.y || getPropValue(window, IFC_PROP.HEIGHT) || 0,
                  assignedWall: getPropValue(window, IFC_PROP.ASSIGNED_WALL) || IFC_PROP.UNKNOWN,
                  dimensions: window.dimensions || { x: 0, y: 0, z: 0 },
                  stringPosition: getPropValue(window, IFC_PROP.POSICION),
                  position: window.position,
                  characteristics: getPropValue(window, IFC_PROP.ESPACIO_CONTIGUO) || IFC_PROP.UNKNOWN,
                  vectors: window.vectors || null,
                  aislation: getPropValue(window, IFC_PROP.AISLACION) == 'CON' ? true : false,
                }
              }),
              elements: walls.map(wall => {
                return {
                  id: wall.id,
                  name: wall.name,
                  area: Number(getPropValue(wall, IFC_PROP.AREA)) || 0,
                  material: getPropValue(wall, IFC_PROP.MATERIAL) || IFC_PROP.UNKNOWN,
                  thickness: Number(getPropValue(wall, IFC_PROP.ESPESOR)) || 0,
                  orientation: getPropValue(wall, IFC_PROP.ORIENTACION),
                  location: getPropValue(wall, IFC_PROP.ESPACIO_CONTIGUO) || IFC_PROP.UNKNOWN,
                  volume: wall.volume || 0,
                  dimensions: wall.dimensions || { x: 0, y: 0, z: 0 },
                  position: wall.position || { x: 0, y: 0, z: 0 },
                  vectors: wall.vectors || null,
                  color: getPropValue(wall, IFC_PROP.COLOR) || 'INTERMEDIO',
                };
              }),
              thermalBridges: thermalBridges
            };
          }),
          floors: floorCodes.map(code => {
            const floors = objects.filter(obj =>
              obj.type.includes(IFC_TYPES.IFCSLab) &&
              obj.props.some((p: any) => p.name === IFC_PROP.WALL_CODE && p.value === code)
            );

            return {
              code: code,
              elements: floors.map(floor => ({
                id: floor.id,
                name: floor.name,
                material: getPropValue(floor, IFC_PROP.MATERIAL) || IFC_PROP.UNKNOWN,
                color: getPropValue(floor, IFC_PROP.COLOR) || IFC_PROP.UNKNOWN,
                thickness: Number(getPropValue(floor, IFC_PROP.ESPESOR)) || 0,
                keyNote: getPropValue(floor, IFC_PROP.NOTACLAVE) || IFC_PROP.UNKNOWN,
                area: Number(getPropValue(floor, IFC_PROP.AREA)) || 0,
                volume: Number(getPropValue(floor, IFC_PROP.AREA)) * Number(getPropValue(floor, IFC_PROP.ESPESOR)) || 0,
                dimensions: floor.dimensions || { x: 0, y: 0, z: 0 },
                position: floor.position || { x: 0, y: 0, z: 0 },
                vectors: floor.vectors || null,
                ventilated: getPropValue(floor, IFC_PROP.PISO_VENTILADO)?.toLowerCase().includes('no') ? false : true,
                perimeter: Number(getPropValue(floor, IFC_PROP.PERIMETRO)) || 0,
                location: getPropValue(floor, IFC_PROP.ESPACIO_CONTIGUO) || IFC_PROP.UNKNOWN,
                aislVertLambda: Number(getPropValue(floor, IFC_PROP.AISL_VERT_LAMBDA)) || 2,
                aislHorizD: Number(getPropValue(floor, IFC_PROP.AISL_HORIZ_D)) || 3,
                aislVertD: Number(getPropValue(floor, IFC_PROP.AISL_VERT_D)) || 1,
                aislHorizLambda: Number(getPropValue(floor, IFC_PROP.AISL_HORIZ_LAMBDA)) || 2,
                aislVertE: Number(getPropValue(floor, IFC_PROP.AISL_VERT_E)) || 2,
                aislHorizE: Number(getPropValue(floor, IFC_PROP.AISL_HORIZ_E)) || 3,
              }))
            };
          }),
          ceilings: ceilingCodes.map(code => {
            const ceilings = objects.filter(obj =>
              obj.type.includes(IFC_TYPES.IFCSLab) &&
              obj.props.some((p: any) => p.name === IFC_PROP.WALL_CODE && p.value === code)
            );
            return {
              code: code,
              elements: ceilings.map(ceiling => ({
                id: ceiling.id,
                name: ceiling.name,
                material: getPropValue(ceiling, IFC_PROP.MATERIAL, name, true),
                color: getPropValue(ceiling, IFC_PROP.COLOR, name, true),
                thickness: Number(getPropValue(ceiling, IFC_PROP.ESPESOR, name, true)),
                keyNote: getPropValue(ceiling, IFC_PROP.NOTACLAVE, name, true),
                area: Number(getPropValue(ceiling, IFC_PROP.AREA, name, true)),
                volume: Number(getPropValue(ceiling, IFC_PROP.AREA, name, true)) * Number(getPropValue(ceiling, IFC_PROP.ESPESOR, name, true)),
                dimensions: ceiling.dimensions || { x: 0, y: 0, z: 0 },
                position: ceiling.position || { x: 0, y: 0, z: 0 },
                vectors: ceiling.vectors || null
              }))
            };
          }),
          doors: doors?.map(door => {
            return {
              id: door.id,
              name: door.name,
              code: getPropValue(door, IFC_PROP.DOOR_CODE, name, true),
              type: door.type || getPropValue(door, 'TIPO') || IFC_PROP.UNKNOWN,
              width: door.dimensions?.x || getPropValue(door.props, IFC_PROP.WIDTH) || 0,
              height: door.dimensions?.y || getPropValue(door.props, IFC_PROP.HEIGHT) || 0,
              assignedWall: getPropValue(door.props, IFC_PROP.ASSIGNED_WALL) || IFC_PROP.UNKNOWN,
              uValue: getPropValue(door.props, 'U') || 0,
              dimensions: door.dimensions || { x: 0, y: 0, z: 0 },
              position: door.position || { x: 0, y: 0, z: 0 },
              vectors: door.vectors || null
            }
          }),

        }
      };
    })
  };

  // Process all objects
  async function processObjectsSequentially(objects: Array<any>) {
    setIsProcessing(true);
    setStatus("Procesando objetos...");
    setIsUploadComplete(false);
    try {
      // Generate structured output
      const building = generateStructuredOutput(objects);
      console.log("Building structure:", building);

      // Use the projectBuilder hook to create the project from the structured data
      setStatus("Creando proyecto...");
      const result = await projectBuilder.createProjectWithValidation(building);
      if (result?.success) {
        setStatus(`Proceso completado: ${result?.completedRooms} recintos creados`);
        notify("Proyecto creado exitosamente");
        setIsUploadComplete(true);
        setIsProcessing(false);
      } else {
        setStatus(`Proceso no logró completarse debido a errores.`);
        console.error("Errors during project creation:", result);
        notify(`Proceso no logró completarse debido a errores`, "error");
        setMissingElements(result.missingElements || []);
        setIsProcessing(false);
        setIsUploadComplete(false);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido durante el procesamiento';
      console.error("Error processing objects:", error);
      setStatus(`Error: ${errorMessage}`);
      notify(`Error: ${errorMessage}", "error`);
      setIsProcessing(false);
      setIsUploadComplete(false);
    }
  }

  // Effects
  useEffect(() => {
    if (router.query.id) {
      console.log("Project ID from router:", router.query.id);
      setProjectId(router.query.id as string);
    }
  }, [router.query.id]);

  useEffect(() => {
    loadIFCViewer()
      .then((IFCViewer) => {
        try {
          setViewerInstance(
            new IFCViewer({ canvasId: "myCanvas", modelPath: "" })
          );
        } catch (error) {
          console.error("Error initializing IFCViewer:", error);
        }
      })
      .catch((error) => {
        console.error("Error loading IFCViewer module:", error);
      });

    // Cleanup function to release memory when component unmounts

    return () => {
      if (viewerInstance) {
        console.log("Cleaning up IFC viewer resources...");
        // Unload any models
        viewerInstance.unloadModel?.();
        // Dispose of the viewer if it has a dispose method
        viewerInstance.dispose?.();
        // Clear the canvas
        const canvas = document.getElementById("myCanvas") as HTMLCanvasElement;
        if (canvas) {
          const ctx = canvas.getContext("2d");
          ctx?.clearRect(0, 0, canvas.width, canvas.height);
        }
        // Force garbage collection by nullifying the reference
        setViewerInstance(null);
      }
    };
  }, []);

  useEffect(() => {
    if (viewerInstance) {
      viewerInstance?.sceneModel?.on("loaded", async () => {
        setObjectsData(await viewerInstance?.objects);
      })
    }
  }, [viewerInstance]);

  // Render component
  return (
    <Card>
      <Row className="mb-4">
        <Col className="text-center">
          <h2>Gestor IFC</h2>
        </Col>
      </Row>
      <IFCUploader onFileUpload={handleFileUpload} />      <Row className="mb-3">
        <Col className="d-flex justify-content-end">
          {fileSelected && !isProcessing && (
            <CustomButton
              onClick={() => processObjectsSequentially(objectsData)}
              disabled={isUploadComplete}
            >
              Procesar Objetos
            </CustomButton>
          )}
        </Col>
      </Row>



      <Container fluid className="p-0">
        <Row className="g-0">
          <Col xs={12} md={6} style={{ height: "50vh", border: '1px solid #ccc', overflowY: 'auto' }}>      <Row className="mb-3">
            <Col className="text-center">
            <h3 style={{ fontSize: '1.5rem', fontWeight: 500 }}>Estructura de archivo</h3>
            </Col>
          </Row>
            <div id="treeViewContainer" style={{ height: "100%" }}></div>
          </Col>
          <Col xs={12} md={6} style={{ height: "50vh", border: '1px solid #ccc' }}>      
            <Col className="text-center">
              <h3 style={{ fontSize: '1.5rem', fontWeight: 500 }}>Modelo 3D</h3>
            </Col>
            <div id="canvasContainer" style={{ height: "100%", width: "100%" }}>
              <canvas id="myCanvas" style={{ width: "100%", height: "100%", display: "block" }} />
            </div>
          </Col>
        </Row>
      </Container>

      {/* Botón para ir a editar workflow part 1 */}
      <Container fluid className="mt-4">
        <Row>
          <Col>
            {status.includes("Proceso completado") && (
              <CustomButton
                color="orange"
                className="mb-3"
                onClick={() => {
                  if (projectId) {
                    router.push(`/workflow-part1-edit?id=${projectId}`);
                  } else {
                    notify("No hay proyecto seleccionado");
                  }
                }}
              >
                Ir a editar datos del proyecto
              </CustomButton>
            )}
          </Col>
        </Row>
        <Row>
          <Col>
            <h5 style={{
              color: status.includes("Error") || status.includes("errores") ? "red" :
                status.includes("Proceso completado") ? "green" :
                  "black"
            }}>
              {isProcessing && <Loader2 size={20} className="me-2" />}
              {status.includes("Proceso completado") && <Check size={20} />}
              {status || "Esperando acción..."}
            </h5>

            {/* Mostrar botón para ver elementos faltantes si hay alguno */}
            {missingElements.length > 0 && !isProcessing && (
              <CustomButton
                onClick={() => setIsProcessing(true)}
                className="btn-warning mt-2"
              >
                Ver {missingElements.length} Elementos Faltantes
              </CustomButton>
            )}
          </Col>
        </Row>

        {/* Detailed status section - Ahora se muestra siempre que haya un estado de creación */}
        {(isProcessing || projectBuilder.creationStatus.completedRooms > 0 || projectBuilder.creationStatus.errors.length > 0) && (
          <ProjectStatusPanel creationStatus={{
            ...projectBuilder.creationStatus,
            missingElements: missingElements
          }} />
        )}

        {/* Error Details Section */}
        {projectBuilder.creationStatus.errors.length > 0 && (
          <ErrorDetailsAccordion errors={projectBuilder.creationStatus.errors} />
        )}

        {/* Missing Elements Panel - Mostrar si hay elementos faltantes y el usuario ha hecho clic en el botón */}
        {missingElements.length > 0 && isProcessing && (
          <MissingElementsPanel
            elements={missingElements}
            onClose={() => setIsProcessing(false)}
          />
        )}
      </Container>

    </Card>
  );
}
