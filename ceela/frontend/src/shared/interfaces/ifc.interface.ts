// IFC-related interfaces for building structure and status tracking

import { ThermalBridge } from './thermalBridge.interface';

// Thermal bridge data extracted from IFC
export interface ThermalBridgeIFC {
    po1_length?: number;
    po1_element?: string;
    po2_length?: number;
    po2_element?: string;
    po3_length?: number;
    po3_element?: string;
    po4_length?: number;
    po4_e_aislacion?: number;
    po4_element?: string;
    fav1?: number;
    fav2?: number;
    fav3?: number;
}

export interface Vector {
    x: number;
    y: number;
    z: number;
}

export interface Vectors {
    length: number;
    width: number;
    height: number;
    minPoint: number[];
    maxPoint: number[];
    center: number[];
}

export interface OccupationProfile {
    code: string;
    type: string;
    occupation: string;
}

export interface RoomProperties {
    roomCode: string;
    roomType: string;
    occupationProfile: OccupationProfile;
    level: string;
    volume: number;
    surfaceArea: number;
    averageHeight: number;
    wallsAverageHeight: number;
    dimensions: Vector;
    position: Vector;
}

export interface Element {
    id: string;
    name: string;
    code?: string;
    material?: string;
    thickness: number;
    area?: number;
    volume?: number;
    color?: string;
    keyNote?: string;
    orientation?: string;
    location?: string;
    dimensions: Vector;
    position: Vector;
    vectors: Vectors;
    ventilated?: boolean;
    perimeter?: number;
}

export interface Window {
    id: string;
    name: string;
    code: string;
    type: string;
    width: number;
    height: number;
    assignedWall: string;
    dimensions: Vector;
    position: Vector;
    stringPosition?: string;
    vectors: Vectors;
    aislation?: boolean;
    characteristics?: string;
}

export interface ConstructionGroup {
    code: string;
    elements: Element[];
    windows?: Window[];
    thermalBridges?: ThermalBridgeIFC[];
}

export interface CeilingElement {
    id: string;
    name: string;
    material: string;
    thickness: number;
    area?: number;
    volume?: number;
    color?: string;
    keyNote?: string;
    dimensions: Vector;
    position: Vector;
    vectors: Vectors;
    
}
export interface FloorElement {
    id: string;
    name: string;
    material: string;
    thickness: number;
    area?: number;
    volume?: number;
    color?: string;
    keyNote?: string;
    dimensions: Vector;
    position: Vector;
    vectors: Vectors;
    ventilated?: boolean;
    perimeter?: number;
    location?: string;
    aislVertLambda?: number;
    aislHorizD?: number;
    aislVertD?: number;
    aislHorizLambda?: number;
    aislVertE?: number;
    aislHorizE?: number;
}


export interface CeilingGroup {
    code: string;
    elements: CeilingElement[];
}

export interface FloorGroup {
    code: string;
    elements: FloorElement[];
}

export interface Door {
    id: string;
    code: string;
    name: string;
    type: string;
    width: number;
    height: number;
    assignedWall: string;
    uValue: string | number;
    dimensions: Vector;
    position: Vector;
    vectors: Vectors;
}

export interface ConstructionDetails {
    walls: ConstructionGroup[]; 
    floors: FloorGroup[];
    ceilings: CeilingGroup[];
    doors: Door[];
}

export interface Room {
    id: string;
    name: string;
    type: string;
    properties: RoomProperties;
    constructionDetails: ConstructionDetails;
}

export interface BuildingStructure {
    buildingStructure: Room[];
}

export interface RoomResponse {
    id: number;
    name: string;
    properties: Record<string, unknown>;
    project_id: number;
}

export interface CreationStatus {
    inProgress: boolean;
    completedRooms: number;
    totalRooms: number;
    totalWalls?: number;
    totalFloors?: number;
    totalCeilings?: number;
    totalDoors?: number;
    totalWindows?: number;
    totalThermalBridges?: number;
    completedThermalBridges?: number;
    currentPhase?: 'walls' | 'floors' | 'ceilings' | 'doors' | 'windows' | 'creating-room';
    currentRoom?: string;
    currentComponent?: string;
    progress: {
        rooms: number;
        walls: number;
        floors: number;
        ceilings: number;
        doors: number;
        windows: number;
        thermalBridges: number;
    };
    missingElements: Array<{ type: string; name: string }>;
    errors: Array<{ context: string; message: string }>;
}
