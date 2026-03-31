import { describe, it, expect } from 'vitest'
import {
    getUnidadPorModulo,
    formatPesoPorModulo,
    convertirParaInput,
    convertirParaBD
} from '@/utils/units'

describe('Utilidades de Unidades (units.ts)', () => {

    describe('getUnidadPorModulo', () => {
        it('debe retornar la unidad configurada para cada módulo', () => {
            expect(getUnidadPorModulo('BALANZA')).toBe('TM')
            expect(getUnidadPorModulo('MUESTREO')).toBe('TM')
            expect(getUnidadPorModulo('LIQUIDACIONES')).toBe('TMC')
            expect(getUnidadPorModulo('MODULO_INVENTADO')).toBe('TM') // Fallback al DEFAULT
        })
    })

    describe('convertirParaInput (De Base de Datos a Vista)', () => {
        it('no debe convertir', () => {
            // 15.5 TM en la BD -> 15500 KG en el input de Balanza
            expect(convertirParaInput(15.5, 'BALANZA')).toBe(15.5)
        })

        it('debe mantener TM para Muestreo (multiplicar x 1)', () => {
            expect(convertirParaInput(15.5, 'MUESTREO')).toBe(15.5)
        })

        it('debe manejar valores nulos o inválidos devolviendo null', () => {
            expect(convertirParaInput(null as any, 'BALANZA')).toBeNull()
            expect(convertirParaInput(undefined as any, 'BALANZA')).toBeNull()
            expect(convertirParaInput(NaN, 'BALANZA')).toBeNull()
        })
    })

    describe('convertirParaBD (De Vista a Base de Datos)', () => {
        it('debe mantener TM para Muestreo (dividir / 1)', () => {
            expect(convertirParaBD(25, 'MUESTREO')).toBe(25)
        })
    })

    describe('formatPesoPorModulo (Formateo de texto)', () => {
        it('debe devolver el string formateado con la unidad correcta', () => {
           // 14 TM -> "14.000 TM" en Muestreo (pidiendo 3 decimales)
            expect(formatPesoPorModulo(14, 'MUESTREO', 3)).toBe('14.000 TM')
        })

        it('debe devolver 0 formateado si el valor es nulo', () => {
            expect(formatPesoPorModulo(null as any, 'BALANZA', 1)).toBe('0.0 TM')
        })
    })
})
