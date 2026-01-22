// Interfaz para puentes térmicos, se agregó wall_id para relacionar con el muro
export interface ThermalBridge {
  id: number;
  wall_id: number; // Identifica el muro asociado
  po1_length: number;
  po1_id_element: number;
  po1_element_name?: string;
  po2_length: number;
  po2_id_element: number;
  po2_element_name?: string;
  po3_length: number;
  po3_id_element: number;
  po3_element_name?: string;
  po4_length: number;
  po4_e_aislacion: number;
  po4_id_element: number;
  po4_element_name?: string;
}
