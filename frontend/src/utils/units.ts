// src/utils/units.ts
import { reactive } from 'vue'

// 1. Nuestra unidad base (Lo que siempre viaja desde y hacia el Backend)
export const UNIDAD_BASE_PESO = 'TM'

// 2. Factores de conversión (1 TM equivale a...)
export const FACTORES_PESO: Record<string, number> = {
    'TM': 1,           // Tonelada Métrica (Base)
    'TMC': 1.10231,    // Tonelada Corta (Short Ton)
    'KG': 1000,        // Kilogramos
}

// 3. Configuración Centralizada por Módulo
// (Esto ahora se carga dinámicamente desde el backend y es reactivo)
export const CONFIG_UNIDADES_MODULOS = reactive<Record<string, string>>({
    'BALANZA': 'TM',
    'MUESTREO': 'TM',         // En muestreo ven toneladas métricas
    'LABORATORIO': 'KG',      // Laboratorio suele usar gramos/kg
    'LIQUIDACIONES': 'TMC',   // Comercial liquida en toneladas cortas
    'DEFAULT': 'TM'
})

// 4. Configuración de Pruebas Metalúrgicas
// usa_cip=true  → genera CIPs ofuscados (CIP-XXXXXX-R1) — comportamiento original
// usa_cip=false → usa el IP del lote con sufijo correlativo (IP-0042-R1)
export const CONFIG_PRUEBAS = reactive({ usa_cip: true })

export function updateUnidadesModulos(config: Record<string, string>) {
    if (config.unidad_balanza) CONFIG_UNIDADES_MODULOS.BALANZA = config.unidad_balanza
    if (config.unidad_muestreo) CONFIG_UNIDADES_MODULOS.MUESTREO = config.unidad_muestreo
    if (config.unidad_laboratorio) CONFIG_UNIDADES_MODULOS.LABORATORIO = config.unidad_laboratorio
    if (config.unidad_liquidaciones) CONFIG_UNIDADES_MODULOS.LIQUIDACIONES = config.unidad_liquidaciones
    if (config.unidad_default) CONFIG_UNIDADES_MODULOS.DEFAULT = config.unidad_default
    // Flag de Pruebas: viene como string "true"/"false" desde la config pública
    if (config.pruebas_usa_cip !== undefined)
        CONFIG_PRUEBAS.usa_cip = config.pruebas_usa_cip !== 'false'
}

/**
 * Convierte un valor de la Base de Datos (TM) a la unidad configurada para el módulo,
 * y le añade su etiqueta.
 * @param valorTM - El peso original en Toneladas Métricas
 * @param modulo - El nombre del módulo (ej. 'MUESTREO')
 * @param decimales - Cantidad de decimales a mostrar
 */
export function formatPesoPorModulo(valorTM: number | null | undefined, modulo: string, decimales: number = 2): string {
    // Determinamos qué unidad le toca a este módulo
    const unidadDestino = CONFIG_UNIDADES_MODULOS[modulo] || CONFIG_UNIDADES_MODULOS['DEFAULT']

    if (valorTM == null || isNaN(valorTM)) {
        return `0.${'0'.repeat(decimales)} ${unidadDestino}`
    }

    // Obtenemos el factor y calculamos
    const factor = FACTORES_PESO[unidadDestino as keyof typeof FACTORES_PESO] || 1
    const valorConvertido = valorTM * factor

    return `${valorConvertido.toFixed(decimales)} ${unidadDestino}`
}

/**
 * Devuelve el símbolo de la unidad configurada para un módulo (ej. 'TM', 'KG')
 * Ideal para usar en los títulos o etiquetas de la interfaz.
 */
export function getUnidadPorModulo(modulo: string): string {
    const unidad = CONFIG_UNIDADES_MODULOS[modulo] ?? CONFIG_UNIDADES_MODULOS['DEFAULT'];

    if (!unidad) {
        throw new Error('DEFAULT no está definido');
    }

    return unidad;
}

/** Convierte un número de la BD (TM) al número que el usuario verá en el input */
export function convertirParaInput(valorTM: number | null | undefined, modulo: string): number | null {
    if (valorTM == null || isNaN(valorTM)) return null
    const unidadDestino = getUnidadPorModulo(modulo)
    const factor = FACTORES_PESO[unidadDestino] || 1
    return valorTM * factor
}

/** Convierte el número digitado por el usuario en el input de vuelta a la BD (TM) */
export function convertirParaBD(valorInput: number | null | undefined, modulo: string): number | null {
    if (valorInput == null || isNaN(valorInput)) return null
    const unidadOrigen = getUnidadPorModulo(modulo)
    const factor = FACTORES_PESO[unidadOrigen] || 1
    return valorInput / factor
}
