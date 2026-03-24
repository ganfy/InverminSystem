import { describe, it, expect, beforeEach } from 'vitest'
import {
    guardarBloqueIP,
    obtenerBloqueIP,
    siguienteIP,
    guardarBloqueTK,
    obtenerBloqueTK,
    siguienteTK,
    encolarLoteOnline,
    obtenerTodosLotesOnline,
    type LoteOnlineData
} from '@/composables/useOfflineQueue'

// 1. Interceptamos la conexión a la base de datos para poder vaciarla
let dbRef: IDBDatabase | null = null
const originalOpen = indexedDB.open.bind(indexedDB)

indexedDB.open = function (name: string, version?: number) {
    const req = originalOpen(name, version)
    req.addEventListener('success', function (this: IDBOpenDBRequest) {
        dbRef = this.result
    })
    return req
}

describe('useOfflineQueue - Generación de Códigos', () => {

    // Antes de cada prueba, limpiamos las "tablas" en lugar de borrar la BD
    // Esto respeta el Singleton de _db y evita el bloqueo (timeout)
    beforeEach(async () => {
        if (dbRef) {
            const stores = [
                'ip_block', 'provacops', 'sesiones_q',
                'tk_block', 'lotes_online_q', 'finalizaciones_q', 'sesiones_cache'
            ]

            // Filtramos solo los stores que ya existen
            const storesToClear = stores.filter(s => dbRef!.objectStoreNames.contains(s))

            if (storesToClear.length > 0) {
                const tx = dbRef.transaction(storesToClear, 'readwrite')
                storesToClear.forEach(store => {
                    tx.objectStore(store).clear()
                })

                await new Promise<void>((resolve, reject) => {
                    tx.oncomplete = () => resolve()
                    tx.onerror = () => reject(tx.error)
                })
            }
        }
    })

    describe('siguienteIP', () => {
        it('debe retornar null si no hay bloque reservado', async () => {
            const ip = await siguienteIP()
            expect(ip).toBeNull()
        })

        it('debe generar IPs secuenciales sin array de conocidos', async () => {
            await guardarBloqueIP({ desde: 100, hasta: 150, anio: 2026 })

            const ip1 = await siguienteIP()
            expect(ip1).toBe('IP-0100')

            const ip2 = await siguienteIP()
            expect(ip2).toBe('IP-0101')
        })

        it('CRÍTICO: debe evitar colisiones respetando los IPs conocidos en memoria', async () => {
            await guardarBloqueIP({ desde: 100, hasta: 200, anio: 2026 })

            const ipsEnMemoria = ['IP-0100', 'IP-0101', 'IP-0105']
            const siguiente = await siguienteIP(ipsEnMemoria)

            expect(siguiente).toBe('IP-0106')
        })

        it('debe tomar en cuenta los lotes offline híbridos en cola para evitar colisiones', async () => {
            await guardarBloqueIP({ desde: 50, hasta: 100, anio: 2026 })

            const loteFicticio: LoteOnlineData = {
                offline_id: 'off-1',
                sesion_id: 1,
                tipo_material: 'oro',
                ip: 'IP-0052', // Este es el mayor
                numero_lote: 1,
                numero_ticket: 'TK-00001',
                pesaje: { peso_inicial: 10, peso_final: 5, sacos: null, granel: true, fecha_inicio: null, fecha_fin: null, es_manual: false, justificacion_manual: null },
                creado_en: new Date().toISOString(),
                synced: false,
                sync_error: null
            }
            await encolarLoteOnline(loteFicticio)

            const ip = await siguienteIP()
            expect(ip).toBe('IP-0053')
        })
    })

    describe('siguienteTK', () => {
        it('debe generar Tickets secuenciales', async () => {
            await guardarBloqueTK({ desde: 500, hasta: 550 })

            const tk1 = await siguienteTK()
            expect(tk1).toBe('TK-00500')

            const tk2 = await siguienteTK()
            expect(tk2).toBe('TK-00501')
        })

        it('CRÍTICO: debe evitar colisiones respetando los Tickets conocidos en memoria', async () => {
            await guardarBloqueTK({ desde: 1000, hasta: 2000 })

            const tksEnMemoria = ['TK-01010']
            const siguiente = await siguienteTK(tksEnMemoria)

            expect(siguiente).toBe('TK-01011')
        })
    })
})
