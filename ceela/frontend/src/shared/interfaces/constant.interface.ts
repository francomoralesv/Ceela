
export interface IConstant {
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
  