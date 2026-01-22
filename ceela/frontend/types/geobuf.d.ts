declare module 'geobuf' {
  export function decode(pbf: any): any;
  export function encode(geojson: any, pbf: any): any;
}