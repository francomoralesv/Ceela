import { constantUrlApiEndpoint } from "@/utils/constant-url-endpoint";
import { notify } from "@/utils/notify";
import axios from "axios";

export async function createDetail(detail_parent_id:string){
    const token = localStorage.getItem("token");
    try {
      if (detail_parent_id){
      const response = await axios.post(
        `${constantUrlApiEndpoint}/user/detail-create/${detail_parent_id}`,
        {
          scantilon_location: "Muro",
          name_detail: "Nuevo Detalle",
          material_id: 0,
          layer_thickness: 0
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        }
      );
      
      if (response.data) {
        notify("Detalle creado exitosamente");
        return true
      }}
    } catch (error) {
      console.error("Error al crear el detalle:", error);
      notify("No puedo crear el detalle");
      return false
    }
}

export async function updateChildDetail(id: string, scantilon_location: string, name_detail: string, material_id: number, layer_thickness: number) {
  const token = getToken();
  const url = `${constantUrlApiEndpoint}/user/details/${id}/update`;
  
  try {
    const response = await axios.put(
      url,
      {
        scantilon_location,
        name_detail,
        material_id,
        layer_thickness
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        }
      }
    );

    if (response.data) {
      notify("Detail updated successfully");
      return true;
    }
    return false;
  } catch (error) {
    console.error("Error updating detail:", error);
    notify("Could not update detail");
    return false;
  }
}


export async function updateDetail(detail_id:string, scantilon_location:string, name_detail:string, material_id:number, layer_thickness:number){
    
}

function getToken() {
  throw new Error("Function not implemented.");
}
