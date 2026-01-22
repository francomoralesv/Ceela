import { useApi } from '@/hooks/useApi';
import { constantUrlApiEndpoint } from '@/utils/constant-url-endpoint';
import { useState } from 'react';
import { useFloorBuilder } from './useFloorBuilder';
import { useWallBuilder } from './useWallBuilder';
import { getMaterialByCode, materialsCache } from './materialUtils';

import {
    Vector,
    Vectors,
    OccupationProfile,
    RoomProperties,
    Element,
    ConstructionGroup,
    ConstructionDetails,
    Room,
    BuildingStructure,
    RoomResponse,
    CreationStatus,
    FloorGroup,
    Window,
    ThermalBridgeIFC
} from '@/shared/interfaces/ifc.interface';
import { orientationToAzimutRange } from '@/utils/azimut';

export const useProjectIfcBuilder = (projectId: string) => {
    const { post, get, put } = useApi();
    const wallBuilder = useWallBuilder(projectId);
    const floorBuilder = useFloorBuilder(projectId);

    // Add a materials cache to avoid repeated API calls

    const [creationStatus, setCreationStatus] = useState<CreationStatus>({
        inProgress: false,
        completedRooms: 0,
        totalRooms: 0,
        progress: {
            rooms: 0,
            walls: 0,
            floors: 0,
            ceilings: 0,
            doors: 0,
            windows: 0,
            thermalBridges: 0
        },
        missingElements: [],
        errors: []
    });
    const validateElementsExistence = async (details: ConstructionDetails) => {
        const missingElements: { type: string; name: string }[] = [];
        const checkExistence = async (type: string, elements: Element[]) => {
            if (!elements || elements.length === 0) return
            for (const element of elements) {
                if (type.toLowerCase() === 'door') {
                    const section = 'door';
                    const door = await wallBuilder.getElementByCodeIfc(section, element?.code as string);
                    if (!door || !door.id) {
                        missingElements.push({ type: 'door', name: element.name+ ', IFC Code: ' + element.code });
                    }
                    continue;
                }
                console.log(`Validating ${JSON.stringify(element)}: ${element.material}`);
                try {
                    if (element?.material && element?.material.toLowerCase() !== 'unknown') {
                        const materialInfo = await getMaterialByCode(element?.material);
                        if (!materialInfo) {
                            missingElements.push({ type, name: element.name+ ', IFC Code: ' + element?.material });
                        } 
                    }
                } catch (error) {
                    console.error(`Error validating material: ${element.material}`, error);
                    missingElements.push({ type, name: element.name+ ', IFC Code: ' + element?.material });
                }
            }
        };

        // Validate walls
        if (details.walls) {
            for (const wallGroup of details.walls) {
                await checkExistence('Wall', wallGroup.elements);
                console.log("Creando windows", wallGroup?.windows)
                if (wallGroup?.windows) {
                    for (const windowElement of wallGroup.windows) {
                        const materialInfo = await wallBuilder.getElementByCodeIfc('window', windowElement?.code);
                        console.log("materialInfo windows", materialInfo)
                        if (!materialInfo) {
                            missingElements.push({ type: 'window', name: windowElement.name+ ', IFC Code: ' + windowElement.code });
                        }
                    }
                }
            }
        }

        // Validate floors
        if (details.floors) {
            for (const floorGroup of details.floors) {
                await checkExistence('Floor', floorGroup?.elements);
            }
        }

        // Validate ceilings
        if (details.ceilings) {
            for (const ceilingGroup of details.ceilings) {
                await checkExistence('Ceiling', ceilingGroup?.elements);
            }
        }

        if(details.doors) {
            await checkExistence('Door', details.doors as unknown as Element[]);
        }

        return {
            missingElements,
            foundMaterials: Object.keys(materialsCache)
        };
    };

    const createProjectWithValidation = async (data: Room[]): Promise<any> => {
        const validationResults = [];

        console.log('buildingStructure data', data);
        for (const room of data) {
            const result = await validateElementsExistence(room.constructionDetails);
            const { missingElements, foundMaterials } = result;

            validationResults.push({
                roomName: room.name,
                foundMaterials
            });

            if (missingElements?.length > 0) {
                console.error('Missing elements:', missingElements);
                return {
                    success: false,
                    message: 'Some elements are missing. Creation process stopped.',
                    missingElements,
                    validationResults
                };
            }
        }
        const projectResult = await createProject(data);
        return {
            ...projectResult,
            validationResults
        };
    };
    /**
     * Parse level number from string (e.g., "00 NIVEL 01" => 1)
     */
    const parseNivel = (nivel: string): number => {
        const match = nivel?.match(/\d+$/);
        return match ? parseInt(match[0], 10) : 0;
    };

    /**
     * Fetch enclosure details by code
     */
    const fetchEnclosureByCode = async (code: string) => {
            const response = await get(`/enclosure-typing/by-code/${code}`);
            return response;
    };

    /**
     * Create a room (enclosure) in the project
     */
    const createRoom = async (room: Room): Promise<RoomResponse> => {
        try {
            // Get occupation data by room code
            const roomName = room.name;
            const occupation = await fetchEnclosureByCode(room.properties.roomCode);
            if (!occupation) {
                throw new Error(`No existe tipo de ocupación ${room.type} para ${roomName}`);
            }
            // Parse level
            const nivel = room.properties.level;
            const piso = parseNivel(nivel);

            // CHANGED: Use roomType instead of name for name_enclosure
            const response = await post(
                `/enclosure-generals-create/${projectId}`,
                {
                    name_enclosure: roomName || 'Default Enclosure',
                    occupation_profile_id: occupation?.id, // Default to ID 1 if not found
                    height: room.properties.averageHeight,
                    co2_sensor: 'No', // Default value
                    level_id: piso
                }
            );

            return {
                id: response.id,
                name: room.name,
                properties: Object.entries(room.properties).reduce((acc, [key, value]) => ({
                    ...acc,
                    [key]: value
                }), {}),
                project_id: parseInt(projectId)
            };
        } catch (error: any) {
            const errorMessage = `${room.name}: ${error?.response?.data?.detail || error?.response?.data}`;
            throw new Error(errorMessage);
        }
    };

    /**
     * Update the creation status with detailed information
     */
    const updateStatus = (updates: Partial<CreationStatus>) => {
        setCreationStatus(prev => ({
            ...prev,
            ...updates,
        }));
    };

    /**
     * Get available thermal bridge detail options from project
     */
    const getThermalBridgeDetailOptions = async () => {
        try {
            const response = await get(`/project/${projectId}/details`);
            return response || [];
        } catch (error) {
            console.warn('Could not fetch thermal bridge detail options:', error);
            return [];
        }
    };

    /**
     * Create thermal bridges for a wall using real project data
     */
    const createThermalBridges = async (enclosureId: number, wallId: number, wallData?: { orientation?: string; area?: number; characteristics?: string }) => {
        try {
            updateStatus({
                currentComponent: `Creando puentes térmicos para muro ID: ${wallId}`
            });

            // Get available detail options for thermal bridge elements
            const detailOptions = await getThermalBridgeDetailOptions();
            
            // Find the first available thermal bridge element or use default
            const defaultElementId = detailOptions.length > 0 ? detailOptions[0].id : 1;
            const defaultElementName = detailOptions.length > 0 ? detailOptions[0].name_detail : undefined;

            // Generate sequential naming for thermal bridges
            const bridgeCounter = creationStatus.progress.thermalBridges + 1;
            const bridgeName = `Esquina ${bridgeCounter}`;

            // Calculate estimated lengths based on wall area (if available)
            const estimatedLength = wallData?.area ? Math.sqrt(wallData.area) * 0.1 : 0; // 10% of wall perimeter estimate

            // Create thermal bridge with real project data
            const thermalBridgeData = {
                wall_id: wallId,
                // Only include mandatory fields with real data
                po1_length: estimatedLength, // Use calculated length or 0
                po1_id_element: defaultElementId,
                // Optional fields - only include if we have real data
                ...(defaultElementName && { po1_element_name: bridgeName }),
                
                po2_length: estimatedLength, // Use same estimated length
                po2_id_element: defaultElementId,
                // Leave po2_element_name empty if no specific data
                
                po3_length: estimatedLength, // Use same estimated length
                po3_id_element: defaultElementId,
                // Leave po3_element_name empty if no specific data
                
                po4_length: estimatedLength, // Use same estimated length
                po4_id_element: defaultElementId,
                po4_e_aislacion: 0 // Required field - leave as 0 if no insulation data
                // Leave po4_element_name empty if no specific data
            };

            const response = await post(`/thermal-bridge-create/${enclosureId}`, thermalBridgeData);
            
            setCreationStatus(prev => ({
                ...prev,
                progress: {
                    ...prev.progress,
                    thermalBridges: prev.progress.thermalBridges + 1
                }
            }));
            
            const wallInfo = wallData ? ` (${wallData.orientation || 'Sin orientación'}, ${wallData.area?.toFixed(2) || 0}m²)` : '';
            updateStatus({
                currentComponent: `Puente térmico "${bridgeName}" creado exitosamente para muro ID: ${wallId}${wallInfo}`
            });

            return { success: true, data: response };
        } catch (error: any) {
            const errorMessage = `Error creando puente térmico para muro ${wallId}: ${error?.response?.data?.detail || error.message || 'Unknown error'}`;
            return {
                success: false,
                error: {
                    message: errorMessage,
                    context: `Thermal bridge creation for wall ID: ${wallId}`
                }
            };
        }
    };

    /**
     * Create walls for a room using wall-enclosures-create endpoint
     */
    const createWalls = async (roomId: number, wallGroups: ConstructionGroup[]) => {
        const wallPromises: Promise<any>[] = [];
        const errors = [];

        try {
            updateStatus({
                currentPhase: 'walls',
                currentComponent: 'Iniciando creación de muros'
            });

            for (const wallGroup of wallGroups) {
                try {
                    updateStatus({ currentComponent: `Creando grupo de muros: ${wallGroup.code}` });

                    // Create a master wall node first
                    const masterNodeName = wallGroup.code;
                    const masterNode = await wallBuilder.createNodeMaster(
                        masterNodeName,
                        'Claro',
                        'Claro',
                        {
                            ...wallGroup,
                            windows: (wallGroup as any).windows ?? []
                        },
                        roomId
                    );

                    for (const element of wallGroup.elements) {
                        try {
                            updateStatus({
                                currentComponent: `Creando capa para muro: ${element.name}`
                            });
                            let materialId = 1;
                            if (element.material && element.material.toLowerCase() !== 'unknown') {
                                updateStatus({
                                    currentComponent: `Buscando material: ${element.material}`
                                });
                                const materialInfo = await getMaterialByCode(element.material);
                                materialId = materialInfo?.id || 1;
                                updateStatus({
                                    currentComponent: `Material encontrado: ${element.material} (ID: ${materialId})`
                                });
                            }
                            const layerThickness = element.thickness;
                            if (masterNode) {
                                await wallBuilder.createNodeChild(
                                    masterNode,
                                    'Muro',
                                    element.name,
                                    materialId,
                                    layerThickness
                                );
                            }
                        } catch (error: any) {
                            errors.push({
                                message: ` ${error?.response?.data?.detail || 'Unknown error'}`,
                                context: `Wall group: ${wallGroup.code}, Element: ${element.name}`
                            });
                        }
                    }
                    const totalArea = Math.max(...wallGroup.elements.map(element => element.area || 0));
                    updateStatus({ currentComponent: `Asociando muro al recinto: ${wallGroup.code}` });

                    const orientation = wallGroup.elements[0]?.orientation || '';
                    const wallCharacteristics = "Exterior";
                    if (masterNode) {
                        wallPromises.push(
                            post(`/wall-enclosures-create/${roomId}`, {
                                wall_id: masterNode.id,
                                characteristics: wallCharacteristics,
                                angulo_azimut: orientationToAzimutRange(orientation),
                                area: totalArea?.toFixed(2) || 0
                            }));
                        
                        // Create thermal bridges for this wall if they exist
                        if (wallGroup.thermalBridges && wallGroup.thermalBridges.length > 0) {
                            const thermalBridgeResult = await createThermalBridgesFromData(masterNode.id, wallGroup.thermalBridges);
                            if (!thermalBridgeResult.success) {
                                errors.push(...thermalBridgeResult.errors);
                            }
                        }
                    }
                    setCreationStatus(prev => ({
                        ...prev,
                        progress: {
                            ...prev.progress,
                            walls: prev.progress.walls + 1
                        }
                    }));
                } catch (error: any) {
                    errors.push({
                        message: `Error creating master wall node: ${error?.response?.data?.detail || 'Unknown error'}`,
                        context: `Wall group: ${wallGroup.code}`
                    });
                }
            }

            const results = await Promise.allSettled(wallPromises);

            results.forEach((result) => {
                if (result.status === 'rejected') {
                    errors.push({
                        message: `Error associating wall with room: ${result.reason?.message || 'Unknown error'}`,
                        context: `Wall association failed`
                    });
                }
            });

            updateStatus({ currentComponent: 'Creación de muros completada' });
            return { success: errors.length === 0, errors };
        } catch (error: any) {
            return {
                success: false,
                errors: [...errors, {
                    message: error.message || 'Unknown error when creating walls',
                    context: 'Creating walls'
                }]
            };
        }
    };

    /**
     * Create thermal bridges for a wall
     */
    const createThermalBridgesFromData = async (wallId: number, thermalBridges: ThermalBridgeIFC[]) => {
        const errors = [];
        
        try {
            updateStatus({
                currentComponent: 'Creando puentes térmicos'
            });

            for (const bridge of thermalBridges) {
                try {
                    const thermalBridgeData = {
                        wall_id: wallId,
                        po1_length: bridge.po1_length || 0,
                        po1_id_element: bridge.po1_element ? parseInt(bridge.po1_element) : null,
                        po1_element_name: bridge.po1_element || '',
                        po2_length: bridge.po2_length || 0,
                        po2_id_element: bridge.po2_element ? parseInt(bridge.po2_element) : null,
                        po2_element_name: bridge.po2_element || '',
                        po3_length: bridge.po3_length || 0,
                        po3_id_element: bridge.po3_element ? parseInt(bridge.po3_element) : null,
                        po3_element_name: bridge.po3_element || '',
                        po4_length: bridge.po4_length || 0,
                        po4_e_aislacion: bridge.po4_e_aislacion || 0,
                        po4_id_element: bridge.po4_element ? parseInt(bridge.po4_element) : null,
                        po4_element_name: bridge.po4_element || ''
                    };

                    await post('/thermal-bridge/create', thermalBridgeData);
                    
                    setCreationStatus(prev => ({
                        ...prev,
                        progress: {
                            ...prev.progress,
                            thermalBridges: prev.progress.thermalBridges + 1
                        }
                    }));
                } catch (error: any) {
                    errors.push({
                        message: `Error creating thermal bridge: ${error?.response?.data?.detail || 'Unknown error'}`,
                        context: `Wall ID: ${wallId}`
                    });
                }
            }

            updateStatus({ currentComponent: 'Creación de puentes térmicos completada' });
            return { success: errors.length === 0, errors };
        } catch (error: any) {
            return {
                success: false,
                errors: [...errors, {
                    message: error.message || 'Unknown error when creating thermal bridges',
                    context: 'Creating thermal bridges'
                }]
            };
        }
    };

    /**
     * Create floors for a room
     */
    const createFloors = async (roomId: number, floorDetailsMaster: FloorGroup[]) => {
        const floorPromises: Promise<any>[] = [];
        const errors = [];

        try {
            updateStatus({
                currentPhase: 'floors',
                currentComponent: 'Iniciando creación de pisos'
            });

            // Fetch floor details from the API
            const floorDetails = await get(`/project/${projectId}/details/Piso`).catch(error => {
                throw new Error(`Error fetching floor details: ${error.message}`);
            });

            for (const floorGroup of floorDetailsMaster) {
                const masterNode = await floorBuilder.createNodeMaster(
                    floorGroup.code,
                    {
                        vertical: {
                            lambda: floorGroup.elements[0].aislVertLambda,
                            e_aisl: floorGroup.elements[0].aislVertE,
                            d: floorGroup.elements[0].aislVertD
                        },
                        horizontal: {
                            lambda: floorGroup.elements[0].aislHorizLambda,
                            e_aisl: floorGroup.elements[0].aislHorizE,
                            d: floorGroup.elements[0].aislHorizD
                        }
                    }
                );
                if (!masterNode) {
                    throw new Error(`Failed to create master floor node for: ${floorGroup.code}`);
                }
                for (const element of floorGroup.elements) {
                    try {
                        updateStatus({
                            currentComponent: `Creando piso: ${element.name}`
                        });
                        console.log("Element material", element.material)
                        console.log("Floor details", floorDetails)
                        const matchedFloor = floorDetails.find((floor: any) => floor.code_ifc === element.material);
                        console.log("Matched floor", matchedFloor)
                        if (!matchedFloor) {
                            try {
                                let materialId = 0;
                                if (element.material) {
                                    const materialInfo = await getMaterialByCode(element.material);
                                    console.log("Piso material info", materialInfo)
                                    materialId = materialInfo?.id
                                    updateStatus({
                                        currentComponent: `Material encontrado para piso: ${element.material} (ID: ${materialId})`
                                    });
                                }
                                const layerThickness = element.thickness || 20; // Default 20cm if not specified
                                await floorBuilder.createNodeChild(
                                    masterNode,
                                    'Piso',
                                    materialId,
                                    layerThickness
                                );

                            } catch (error: any) {
                                errors.push({
                                    message: `Error creating floor: ${error?.message || 'Unknown error'}`,
                                    context: `Floor group: ${floorGroup.code}, Element: ${element.name}`
                                });
                                continue;
                            }
                        }
                        setCreationStatus(prev => ({
                            ...prev,
                            progress: {
                                ...prev.progress,
                                floors: prev.progress.floors + 1
                            }
                        }));
                    } catch (error: any) {
                        errors.push({
                            message: `Error creating floor element: ${error?.response?.data?.detail || 'Unknown error'}`,
                            context: `Floor group: ${floorGroup.code}, Element: ${element.name}`
                        });
                    }
                }
                const location = floorGroup.elements[0]?.location
    ? floorGroup.elements[0].location[0].toUpperCase() + floorGroup.elements[0].location.slice(1).toLowerCase()
    : 'Exterior';
                
                try {
                    await post(`/floor-enclosures-create/${roomId}`, {
                        floor_id: masterNode.id,
                        characteristic: location,
                        area: floorGroup.elements[0]?.area || 0,
                        value_u: masterNode.value_u,
                        is_ventilated: floorGroup.elements[0]?.ventilated ? 'Ventilado' : 'No ventilado',
                        calculations: masterNode.calculations || {},
                        parameter: floorGroup.elements[0]?.perimeter || 0,
                    });
                } catch (error: any) {
                    errors.push({
                        message: `Error associating floor with room: ${error?.response?.data?.detail || 'Unknown error'}`,
                        context: `Floor group: ${floorGroup.code}`
                    });
                }
            }

            setCreationStatus(prev => ({
                ...prev,
                progress: {
                    ...prev.progress,
                    floors: prev.progress.floors + 1
                }
            }));
            updateStatus({ currentComponent: 'Creación de pisos completada' });
            return { success: errors.length === 0, errors };
        } catch (error: any) {
            console.log("Error creating floors", error)
            return {
                success: false,
                errors: [...errors, {
                    message: error?.response?.data?.detail || 'Unknown error when creating floors',
                    context: 'Creating floors'
                }]
            };
        }
    };

    /**
     * Create ceilings for a room
     */
    const createCeilings = async (roomId: number, ceilingGroups: ConstructionGroup[]) => {
        const ceilingPromises: Promise<any>[] = [];
        const errors = [];

        try {
            updateStatus({
                currentPhase: 'ceilings',
                currentComponent: 'Iniciando creación de techos'
            });

            for (const ceilingGroup of ceilingGroups) {

                const ceilingResponse = await post(
                    `/user/Techo/detail-part-create?project_id=${projectId}`,
                    {
                        name_detail: `TECHO ${ceilingGroup.code}`,
                        scantilon_location: 'Techo'
                    }
                );
                for (const element of ceilingGroup.elements) {
                    try {
                        updateStatus({
                            currentComponent: `Creando techo: ${element.name}`
                        });
                        console.log('Ceiling element:', element);
                        // Handle missing material - try to fetch if not in cache
                        let materialId = 0; // Default material ID
                        if (element.material && element.material.toLowerCase() !== 'unknown') {
                            if (!materialsCache[element.material]?.id) {
                                try {
                                    // Use fetch as requested
                                    const token = localStorage.getItem('token');
                                    const code = element.material;
                                    const response = await fetch(
                                        `${constantUrlApiEndpoint}/constants-code_ifc?code_ifc=${code}`,
                                        {
                                            method: "GET",
                                            headers: {
                                                "Content-Type": "application/json",
                                                Authorization: `Bearer ${token}`,
                                            },
                                        }
                                    );
                                    const materialInfo = await response.json();
                                    if (materialInfo?.id) {
                                        materialsCache[element.material] = materialInfo;
                                        materialId = materialInfo.id;
                                        updateStatus({
                                            currentComponent: `Material encontrado para techo: ${element.material} (ID: ${materialId})`
                                        });
                                    }
                                } catch (error) {
                                    updateStatus({
                                        currentComponent: `Error al buscar material de techo: ${element.material}`
                                    });
                                    console.warn(`Material not found for ceiling code: ${element.material}, using default ID 113`, error);
                                    errors.push({
                                        message: `Material de techo no encontrado: ${element.material}`,
                                        context: `Ceiling element: ${element.name}`
                                    });
                                }
                            } else {
                                materialId = materialsCache[element.material].id;
                            }
                        }
                        if (ceilingResponse)
                            await post(
                                `/user/detail-create/${ceilingResponse.id}`,
                                {
                                    layer_thickness: element.thickness ,
                                    material_id: materialId,
                                    name_detail: element.name,
                                    scantilon_location: 'Techo'
                                }
                            );


                        setCreationStatus(prev => ({
                            ...prev,
                            progress: {
                                ...prev.progress,
                                ceilings: prev.progress.ceilings + 1
                            }
                        }));
                    } catch (error: any) {
                        errors.push({
                            message: `Error creating ceiling: ${error?.response?.data?.detail || 'Unknown error'}`,
                            context: `Ceiling: ${element.name}`
                        });
                    }
                }

                try {
                    await post(`/roof-enclosures-create/${roomId}`, {
                        roof_id: ceilingResponse.id,
                        characteristic: 'Exterior', // Default value
                        area: ceilingGroup.elements[0].area || 0
                    });
                } catch (error: any) {
                    console.log("Error associating ceiling with room", error)
                    errors.push({
                        message: `Error associating ceiling with room: ${error?.response?.data?.detail || 'Unknown error'}`,
                        context: `Ceiling group: ${ceilingGroup.code}`
                    });
                }
            }

            updateStatus({ currentComponent: 'Creación de techos completada' });
            return { success: errors.length === 0, errors };
        } catch (error: any) {
            return { success: false, errors: [{ message: error?.message || 'Unknown error' }] };
        }
    };

    /**
     * Create doors for a room
     */
    // Crear puertas validando existencia por code_ifc
    const createDoors = async (roomId: number, doors: any[]) => {
        const doorPromises: Promise<any>[] = [];
        const errors = [];

        try {
            updateStatus({
                currentPhase: 'doors',
                currentComponent: 'Iniciando creación de puertas'
            });

            console.log("Creating doors :", doors);
            for (const door of doors) {
                const section = 'door';
                let element;
                try {
                    element = await wallBuilder.getElementByCodeIfc(section, door.code);
                } catch (e) {
                    errors.push({
                        message: `Error consultando existencia de puerta codigo ifc=${door.code}`,
                        context: `Puerta ${door.name}`
                    });
                    continue;
                }
                if (!element || !element.id) {
                    errors.push({
                        message: `No existe puerta con codigo ifc=${door.code}`,
                        context: `Puerta ${door.name}`
                    });
                    continue;
                }
                try {
                    const payload = {
                        angulo_azimut: orientationToAzimutRange(door.orientation),
                        orientacion: 'Exterior',
                        door_id: element.id,
                        broad: door.width || 0,
                        high: door.height || 0,
                        characteristics: door.name || ''
                    };
                    doorPromises.push(
                        post(`/door-enclosures-create/${roomId}`, {
                            ...payload,
                            enclosure_id: roomId
                        })
                    );
                    setCreationStatus(prev => ({
                        ...prev,
                        progress: {
                            ...prev.progress,
                            doors: prev.progress.doors + 1
                        }
                    }));
                } catch (err: any) {
                    errors.push({
                        message: `Error creando puerta : ${err && err.message ? err.message : String(err)}`,
                        context: `Puerta ${door.name}`
                    });
                }
            }

            const _results = await Promise.allSettled(doorPromises);
            updateStatus({ currentComponent: 'Creación de puertas completada' });

            return { success: errors?.length === 0, errors };
        } catch (error: any) {
            return {
                success: false,
                errors: [...errors, {
                    message: error.message || 'Unknown error when creating doors',
                    context: 'Creating doors'
                }]
            };
        }
    };
    // durante la creación de muros en useWallBuilder.tsx -> createNodeMaster

    /**
     * Create room details (walls, floors, ceilings, doors, windows)
     */
    const createRoomDetails = async (roomId: number, details: ConstructionDetails, roomName: string) => {
        const errors = [];
        console.log("roomId: ", roomId)
        console.log("details: ", details)
        updateStatus({
            currentRoom: roomName,
            currentPhase: 'creating-room',
            currentComponent: `Iniciando creación de detalles para recinto: ${roomName}`
        });

        // Create walls
        if (details.walls && details.walls.length > 0) {
            const wallResult = await createWalls(roomId, details.walls);
            if (!wallResult?.success || wallResult?.errors.length > 0) {
                errors.push(...wallResult.errors);
            }
        }

        // Create floors
        if (details.floors && details.floors.length > 0) {
            const floorResult = await createFloors(roomId, details.floors);
            if (!floorResult.success || floorResult.errors.length > 0) {
                errors.push(...floorResult.errors);
            }
        }

        // Create ceilings
        if (details.ceilings && details.ceilings.length > 0) {
            const ceilingResult = await createCeilings(roomId, details.ceilings);
            if (!ceilingResult.success || ceilingResult.errors.length > 0) {
                errors.push(...ceilingResult.errors);
            }
        }

        // Create doors (if any)
        if (details.doors && details.doors.length > 0) {
            const doorResult = await createDoors(roomId, details.doors);
            if (!doorResult?.success || doorResult?.errors.length > 0) {
                errors.push(...doorResult.errors);
            }
        }

        updateStatus({
            currentComponent: `Detalles para recinto ${roomName} completados`,
            currentPhase: undefined
        });

        return { success: errors.length === 0, errors };
    };

    /**
     * Create a complete project from the building structure
     */
    const createProject = async (data: Room[]) => {
        const allErrors: { context: string; message: any; }[] = [];

        // Calculate totals for progress tracking
        const totalWalls = data.reduce((sum, room) => sum + (room.constructionDetails.walls?.length || 0), 0);
        const totalFloors = data.reduce((sum, room) => sum + (room.constructionDetails.floors?.length || 0), 0);
        const totalCeilings = data.reduce((sum, room) => sum + (room.constructionDetails.ceilings?.length || 0), 0);
        const totalDoors = data.reduce((sum, room) => sum + (room.constructionDetails.doors?.length || 0), 0);
        const totalWindows = data.reduce((sum, room) => {
            return sum + (room.constructionDetails.walls?.reduce((wallSum, wall) => {
                return wallSum + ((wall as any).windows?.length || 0);
            }, 0) || 0);
        }, 0);
        const totalThermalBridges = data.reduce((sum, room) => {
            return sum + (room.constructionDetails.walls?.reduce((wallSum, wall) => {
                return wallSum + (wall.thermalBridges?.length || 0);
            }, 0) || 0);
        }, 0);

        setCreationStatus({
            inProgress: true,
            completedRooms: 0,
            totalRooms: data.length,
            totalWalls,
            totalFloors,
            totalCeilings,
            totalDoors,
            totalWindows,
            totalThermalBridges,
            currentPhase: undefined,
            currentRoom: undefined,
            currentComponent: 'Iniciando creación del proyecto',
            progress: {
                rooms: 0,
                walls: 0,
                floors: 0,
                ceilings: 0,
                doors: 0,
                windows: 0,
                thermalBridges: 0
            },
            missingElements: [],
            errors: []
        });

        try {
            for (let i = 0; i < data.length; i++) {
                const room = data[i];

                try {
                    updateStatus({
                        currentRoom: room.name,
                        currentPhase: 'creating-room',
                        currentComponent: `Creando recinto: ${room.name} (${i + 1}/${data.length})`
                    });

                    const createdRoom = await createRoom(room).catch(error => {
                        throw new Error(`Failed to create room: ${error.message}`);
                    });
                    setCreationStatus(prev => ({
                        ...prev,
                        progress: {
                            ...prev.progress,
                            rooms: prev.progress.rooms + 1
                        }
                    }));

                    // Create room construction details
                    const detailsResult = await createRoomDetails(
                        createdRoom.id,
                        room.constructionDetails,
                        room.name
                    );

                    if (!detailsResult.success) {
                        detailsResult.errors.forEach(error =>
                            allErrors.push({
                                ...error,
                                context: `Room ${room.name}: ${error?.message || 'Unknown error'}`
                            })
                        );
                    }

                    // Update status for this room's completion
                    setCreationStatus(prev => ({
                        ...prev,
                        completedRooms: prev.completedRooms + 1
                    }));

                } catch (error) {
                    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                    allErrors.push({
                        message: errorMessage,
                        context: `Room: ${room.name}`
                    });

                    // Update status to include this room as completed (though with error)
                    setCreationStatus(prev => ({
                        ...prev,
                        completedRooms: prev.completedRooms + 1
                    }));
                }
            }

            // Update final creation status with all collected errors
            setCreationStatus(prev => ({
                ...prev,
                inProgress: false,
                currentRoom: undefined,
                currentPhase: undefined,
                currentComponent: 'Creación del proyecto completada',
                errors: allErrors
            }));

            return {
                success: allErrors.length === 0,
                completedRooms: data.length,
                totalRooms: data.length,
                errors: allErrors
            };

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            console.error(`Error creating project: ${errorMessage}`, error);

            const finalErrors = [...allErrors, {
                message: `Error creating project: ${errorMessage}`,
                context: 'Project creation'
            }];

            setCreationStatus(prev => ({
                ...prev,
                inProgress: false,
                currentRoom: undefined,
                currentPhase: undefined,
                currentComponent: 'Error en la creación del proyecto',
                errors: finalErrors
            }));

            return {
                success: false,
                completedRooms: creationStatus.completedRooms,
                totalRooms: data.length,
                errors: finalErrors
            };
        } finally {
            setCreationStatus(prev => ({
                ...prev,
                inProgress: false
            }));
        }
    };

    /**
     * Updates the status of the project
     * @param status The new status to set for the project
     * @returns A promise that resolves when the status has been updated
     */
    const updateProjectStatus = async (status: string): Promise<void> => {
        if (!projectId) {
            throw new Error("Project ID is required to update status");
        }

        try {
            await put(`/project/${projectId}/status`, { status });
        } catch (error) {
            console.error('Error updating project status:', error);
            throw error;
        }
    };

    return {
        createProject,
        creationStatus,
        parseNivel,
        fetchEnclosureByCode,
        updateProjectStatus,
        createProjectWithValidation,
        materialsCache
    };
}