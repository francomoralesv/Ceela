// src/lib/utils.ts

import { notify } from '@/utils/notify';
import React from "react";

export function cn(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}


/**
 * Gets the value of a property from an object's props array. If not found and roomName is provided, shows an error notification.
 * @param obj Object with a props array.
 * @param key Property name to search for.
 * @param roomName (Optional) Name of the room for error notification context.
 * @returns The property value as a string, or '' if not found.
 */
export function getPropValue(
  obj: { props: Array<{ name: string; value: any }> },
  key: string,
  roomName?: string,
  breakIfNotFound: boolean=false
): string {
  const prop = obj.props?.find(p => p.name.toLowerCase() === key.toLowerCase());
  const value = prop?.value?.toString() || '';
  if (value === '' && roomName) {
    notify(`el elemento de nombre ${key} no se encuentra en el recinto de nombre ${roomName}`, 'error',2000);
    if (breakIfNotFound) {
      throw new Error(`el elemento de nombre ${key} no se encuentra en el recinto de nombre ${roomName}`);
    } 
  }
  return value;
}


/**
 * Busca objetos en un array por tipo y una propiedad específica.
 * @param objects - Array de objetos a buscar.
 * @param type - Tipo del objeto (e.g., "IfcWallStandardCase").
 * @param propName - Nombre de la propiedad a buscar (e.g., "CÓDIGO MULTICAPA").
 * @param propValue - Valor de la propiedad a buscar (e.g., "MURO_03").
 * @returns Array de objetos que coinciden con los criterios.
 */
export function findObjectsByTypeAndProperty(
  objects: Array<any>,
  type: string,
  propName: string,
  propValue: string
): Array<any> {
  return objects.filter(
    (obj) =>
      obj.type === type &&
      obj.props.some((prop: any) => prop.name === propName && prop.value === propValue)
  );
}



export function convertAngleToOrientation(angle: number): string {
  // Normalize the angle between 0 and 360
  angle = angle % 360;
  if (angle < 0) angle += 360;

  // Determine the orientation based on the angle
  if (angle >= 0 && angle < 22.5) return "N";
  if (angle >= 22.5 && angle < 67.5) return "NE";
  if (angle >= 67.5 && angle < 112.5) return "E";
  if (angle >= 112.5 && angle < 157.5) return "SE";
  if (angle >= 157.5 && angle < 202.5) return "S";
  if (angle >= 202.5 && angle < 247.5) return "SO";
  if (angle >= 247.5 && angle < 292.5) return "O";
  if (angle >= 292.5 && angle < 337.5) return "NO";
  return "N"; // If it's between 337.5 and 360, it returns "N"
}

export const preventDash = (
    e: React.KeyboardEvent<HTMLInputElement | HTMLSelectElement>
) => {
  if (e.key === "-") e.preventDefault();
};