export interface AnalisisLeyCreate {
    cip: string;
    laboratorio: string;
    tipo_analisis: string; // 'planta', 'externo', 'minero', 'dirimencia'
    material?: string;
    ley_fino: number;
    ley_grueso: number;
    origen_datos?: string;
    fecha_analisis?: string;
}

export interface AnalisisLeyOut extends AnalisisLeyCreate {
    id: number;
    lote_id: number;
    ley_final: number;
    ley_gr_tm: number;
    vigente: boolean;
    certificado_url?: string | null;
}

export interface AnalisisRecuperacionCreate {
    cip: string;
    laboratorio: string;
    ley_cabeza: number;
    ley_cola: number;
    ley_liquido: number;
    origen_datos?: string;
    fecha_analisis?: string;
}

export interface AnalisisRecuperacionOut extends AnalisisRecuperacionCreate {
    id: number;
    lote_id: number;
    recuperacion: number;
    vigente: boolean;
    certificado_url?: string | null;
}

export interface MuestraLaboratorioItem {
    cip: string;
    fecha_envio: string;
    tipo_muestra: string;
    estado_ley: 'PENDIENTE' | 'COMPLETADO';
    estado_recuperacion: 'PENDIENTE' | 'COMPLETADO';
}
