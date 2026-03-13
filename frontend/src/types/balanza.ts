export type TipoDocumento =
    | 'GUIA_REMISION'
    | 'GUIA_TRANSPORTE'
    | 'LICENCIA_CONDUCIR'
    | 'OTRO'

export const TIPO_DOCUMENTO_LABELS: Record<TipoDocumento, string> = {
    GUIA_REMISION: 'Guía de Remisión (GRR)',
    GUIA_TRANSPORTE: 'Guía de Transporte (GRT)',
    LICENCIA_CONDUCIR: 'Licencia de Conducir',
    OTRO: 'Otro documento',
}

export interface DocumentoRespuesta {
    id: number
    sesion_id: number
    tipo_documento: TipoDocumento
    nombre_original: string
    ruta_archivo: string
    creado_en: string | null
}

export interface DatosExtraidos {
    placa: string | null
    carreta: string | null
    conductor: string | null
    transportista: string | null
    razon_social: string | null
    ruc_proveedor: string | null
    guia_remision: string | null
    guia_transporte: string | null
    peso_declarado_tm: number | null
    documentos_detectados: string[]
}
