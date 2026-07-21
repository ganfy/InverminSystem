/**
 * cipGenerator.ts
 * ===============
 * Porta exacta del algoritmo Python `generar_base_cip` de:
 *   backend/app/services/muestreo.py
 *
 * CRÍTICO: Esta función DEBE mantenerse en sincronía con el backend.
 * Si se modifica el algoritmo en Python, actualizar también aquí.
 *
 * Propósito: permitir generar CIPs offline con el mismo código que
 * el servidor hubiera generado, garantizando consistencia en BD.
 */

const CONTROL_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ'

/**
 * Genera la base de 7 caracteres del CIP (6 dígitos + 1 letra de control).
 * Porta exacta de: services/muestreo.py → generar_base_cip(lote_id, salt)
 *
 * @param loteId  - ID numérico del lote (campo `lote_id` del servidor)
 * @param salt    - Correlativo del CIP (1, 2, 3...) para diferenciar CIPs del mismo lote
 * @returns Base como "058598D"
 */
export function generarBaseCip(loteId: number, salt: number): string {
    // LCG (Linear Congruential Generator) — misma fórmula que Python
    const numero = (loteId * 9301 + 49297 + salt * 1337) % 1_000_000
    const base = String(numero).padStart(6, '0')

    // Dígito de control: suma de dígitos, índice en CONTROL_CHARS
    const suma = base.split('').reduce((acc, d) => acc + parseInt(d, 10), 0)
    const control = CONTROL_CHARS[suma % CONTROL_CHARS.length]

    return `${base}${control}`
}

/**
 * Genera el código CIP completo para un lote.
 * Porta exacta del código final en generar_cips_para_lote:
 *   f"CIP-{generar_base_cip(lote.id, salt=correlativo)}-A{correlativo}"
 *
 * @param loteId      - ID numérico del lote
 * @param correlativo - Número de CIP para este lote (empieza en 1)
 * @returns Código como "CIP-058598D-A1"
 */
export function generarCodigoCip(loteId: number, correlativo: number): string {
    return `CIP-${generarBaseCip(loteId, correlativo)}-A${correlativo}`
}

/**
 * Determina el laboratorio destino según el correlativo.
 * Porta la lógica de generar_cips_para_lote:
 *   laboratorio = "Paititi" if correlativo <= 2 else "Por definir"
 */
export function laboratorioParaCip(correlativo: number): string {
    return correlativo <= 2 ? 'Paititi' : 'Por definir'
}

/**
 * Genera el par de CIPs de recuperación para una prueba metalúrgica.
 *
 * El contador de correlativo es INDEPENDIENTE del de muestreo (sufijo A).
 * Los CIPs de recuperación usan sufijo 'R' (RecuperacionInterno) o 'E' (RecuperacionExterno).
 *
 * Porta la lógica de services/pruebas.py → etiquetar_prueba:
 *   correlativo1 = total_cips_rec + 1
 *   correlativo2 = total_cips_rec + 2
 *   codigo = f"CIP-{generar_base_cip(lote.id, salt=correlativo)}-{sufijo}{correlativo}"
 *
 * @param loteId           - ID numérico del lote
 * @param totalCipsRec     - Cuántos CIPs de recuperación (R o E) ya existen para este lote
 * @param tipo             - 'RecuperacionInterno' (default) | 'RecuperacionExterno'
 * @returns Par { cip1, cip2, correlativo1, correlativo2, sufijo }
 */
export function generarParCipsRecuperacion(
    loteId: number,
    totalCipsRec: number,
    tipo: 'RecuperacionInterno' | 'RecuperacionExterno' = 'RecuperacionInterno',
): { cip1: string; cip2: string; correlativo1: number; correlativo2: number; sufijo: string } {
    const sufijo = tipo === 'RecuperacionInterno' ? 'R' : 'E'

    const correlativo1 = totalCipsRec + 1
    const correlativo2 = totalCipsRec + 2

    const cip1 = `CIP-${generarBaseCip(loteId, correlativo1)}-${sufijo}${correlativo1}`
    const cip2 = `CIP-${generarBaseCip(loteId, correlativo2)}-${sufijo}${correlativo2}`

    return { cip1, cip2, correlativo1, correlativo2, sufijo }
}
