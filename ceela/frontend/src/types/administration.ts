export interface MaterialAttributes {
  name: string;
  conductivity: number;
  specific_heat: number;
  density: number;
}

export interface Material {
  id: number;
  atributs: MaterialAttributes;
  material_id?: number;
  name?: string;
  type?: string;
  is_deleted?: boolean;
  create_status?: string;
}

export interface Detail {
  id?: number;

  id_detail?: number;
  scantilon_location: string;
  name_detail: string;
  material_id: number;
  layer_thickness: number;
  created_status?: string;
  is_deleted?: boolean;
}

export interface ElementAttributesDoor {
  u_puerta_opaca: number;
  porcentaje_vidrio: number;
  ventana_id: number;
  name_ventana: string;
}

export interface ElementAttributesWindow {
  u_vidrio: number;
  fs_vidrio: number;
  frame_type: string;
  clousure_type: string;
}

export type ElementAttributes = ElementAttributesDoor | ElementAttributesWindow;

export interface Element {
  code_ifc: string;
  id: number;
  type: "door" | "window";
  name_element: string;
  u_marco: number;
  fm: number;
  atributs: ElementAttributes;
}
