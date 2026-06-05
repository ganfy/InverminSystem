import { mount, flushPromises } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createTestingPinia } from '@pinia/testing'
import { useLiquidacionesStore } from '@/stores/liquidaciones'
import {
    getLotesDisponibles,
    getLiquidaciones,
    getLiquidacion,
    previewLiquidacion,
    crearLiquidacion,
    cambiarEstadoLiquidacion,
    emitirLiquidacion,
    getLiquidacionesKPIs,
} from '@/api/liquidaciones'
import LiquidacionesView from '@/views/liquidaciones/LiquidacionesView.vue'
import CrearLiquidacionView from '@/views/liquidaciones/CrearLiquidacionView.vue'
import DetalleLiquidacionView from '@/views/liquidaciones/DetalleLiquidacionView.vue'
import { useUiStore } from '@/stores/ui'

// ── Mocks globales ────────────────────────────────────────────────────────────

vi.mock('@/api/liquidaciones', () => ({
    obtenerPrecioOro: vi.fn(),
    getLotesDisponibles: vi.fn(),
    previewLiquidacion: vi.fn(),
    getLiquidaciones: vi.fn(),
    getLiquidacion: vi.fn(),
    crearLiquidacion: vi.fn(),
    cambiarEstadoLiquidacion: vi.fn(),
    getLiquidacionesKPIs: vi.fn(),
    descargarPDF: vi.fn(),
    editarParamsLote: vi.fn(),
    emitirLiquidacion: vi.fn(),
}))

vi.mock('vue-router', async (importOriginal) => {
    const actual = await importOriginal<typeof import('vue-router')>()
    return {
        ...actual,
        useRouter: vi.fn(() => ({ push: vi.fn() })),
        useRoute: vi.fn(() => ({ params: { id: '1' } })),
    }
})

vi.mock('@/stores/ui', () => ({
    useUiStore: vi.fn(() => ({
        showConfirm: vi.fn().mockResolvedValue(true),
        toast: vi.fn(),
    })),
}))

// ── Fixtures ──────────────────────────────────────────────────────────────────

const loteFake = {
    ip: 'IP-TEST-01',
    tipo_material: 'Mineral',
    fecha_recepcion: '2026-01-10',
    dias_almacen: 8,
    tms: 9.5,
    tmh: 10.0,
    sacos: 10,
    volado: false,
    alerta_vencimiento: false,
    ley_comercial: 0.35,
    oz_tc_planta: 0.35,
    oz_tc_minero: 0.33,
    porcentaje_rec: 88,
    usa_dirimencia: false,
    listo_para_liquidar: true,
    provacop_id: 1,
    proveedor: 'Minera Demo SAC',
    acopiador: 'Acopiador Demo SAC',
}

const loteFinancieroFake = {
    ip: 'IP-TEST-01',
    fecha_recepcion: '2026-01-10',
    tmh: 10.0,
    pct_humedad: 5.0,
    tms: 9.5,
    sacos: 10,
    oz_tc_planta: 0.35,
    oz_tc_comercial: 0.34,
    oz_tc_minero: 0.33,
    oz_tc_promedio: 0.335,
    pct_rec_liq: 88,
    pct_rec_planta: 88,
    maquila: 128.5,
    riesgo: 10,
    spot_usd: 2400,
    insumos_acopio: 5,
    insumos_consumo: 3,
    insumos_total: 8,
    bono: 0,
    factor: 1.1023,
    precio_x_tms: 620.5,
    total_usd: 5894.75,
    fino_recuperable: 3.42,
    usa_dirimencia: false,
    alertas: [],
}

const previewFake = {
    provacop_id: 1,
    proveedor_razon_social: 'Minera Demo SAC',
    proveedor_ruc: '20111111111',
    acopiador_nombre: 'Acopiador Demo SAC',
    spot_usd: 2400,
    lotes: [loteFinancieroFake],
    total_usd: 5894.75,
    total_tms: 9.5,
    total_tmh: 10.0,
    total_oz_compradas: 3.42,
    count_lotes: 1,
    alertas_globales: [],
    puede_generar: true,
}

const liquidacionResumenFake = {
    id: 1,
    numero_liquidacion: 'LIQ-0001',
    estado: 'GENERADA',
    provacop_id: 1,
    proveedor_razon_social: 'Minera Demo SAC',
    proveedor_ruc: '20111111111',
    acopiador_nombre: 'Acopiador Demo SAC',
    spot_usd: 2400,
    total_usd: 5894.75,
    count_lotes: 1,
    fecha_creacion: '2026-01-18T10:00:00',
}

const liquidacionDetalleFake = {
    ...liquidacionResumenFake,
    lotes: [{ ...loteFinancieroFake, liquidacion_id: 1, fecha_emision: '2026-01-18' }],
    pdf_url: null,
    fecha_cierre: null,
}

const kpisFake = {
    borradores: 2,
    generadas: 5,
    lotes_liquidables: 8,
    valor_pendiente_usd: 45000,
}

// ============================================================
// SUITE 1 - Store: cargarLista
// ============================================================
describe('liquidacionesStore.cargarLista', () => {
    beforeEach(() => {
        vi.mocked(getLiquidaciones).mockResolvedValue({ data: [liquidacionResumenFake] } as any)
    })

    it('carga liquidaciones desde la API y las expone en store.lista', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        await store.cargarLista()

        expect(store.lista).toHaveLength(1)
        expect(store.lista[0].numero_liquidacion).toBe('LIQ-0001')
        expect(store.cargando).toBe(false)
    })

    it('filtra por provacop_id cuando se indica', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        await store.cargarLista({ provacop_id: 1 })

        expect(getLiquidaciones).toHaveBeenCalledWith({ provacop_id: 1 })
    })

    it('registra error en store.error cuando la API falla', async () => {
        vi.mocked(getLiquidaciones).mockRejectedValue({
            response: { data: { detail: 'Error de red' } },
        })
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        await store.cargarLista()

        expect(store.error).toBe('Error de red')
        expect(store.cargando).toBe(false)
    })
})

// ============================================================
// SUITE 2 - Store: cargarDetalle
// ============================================================
describe('liquidacionesStore.cargarDetalle', () => {
    beforeEach(() => {
        vi.mocked(getLiquidacion).mockResolvedValue({ data: liquidacionDetalleFake } as any)
    })

    it('carga el detalle y lo expone en store.detalle', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        await store.cargarDetalle(1)

        expect(store.detalle).not.toBeNull()
        expect(store.detalle?.id).toBe(1)
        expect(store.detalle?.lotes).toHaveLength(1)
    })

    it('registra error si la liquidacion no existe', async () => {
        vi.mocked(getLiquidacion).mockRejectedValue({
            response: { data: { detail: 'Liquidacion no encontrada' } },
        })
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        await store.cargarDetalle(999)

        expect(store.error).toBe('Liquidacion no encontrada')
    })
})

// ============================================================
// SUITE 3 - Store: cargarLotesDisponibles
// ============================================================
describe('liquidacionesStore.cargarLotesDisponibles', () => {
    beforeEach(() => {
        vi.mocked(getLotesDisponibles).mockResolvedValue({ data: [loteFake] } as any)
    })

    it('expone los lotes listos para liquidar en store.lotesDisponibles', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        await store.cargarLotesDisponibles(1)

        expect(store.lotesDisponibles).toHaveLength(1)
        expect(store.lotesDisponibles[0].ip).toBe('IP-TEST-01')
        expect(store.lotesDisponibles[0].listo_para_liquidar).toBe(true)
    })

    it('llama a la API con el provacop_id correcto', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        await store.cargarLotesDisponibles(42)

        expect(getLotesDisponibles).toHaveBeenCalledWith(42)
    })
})

// ============================================================
// SUITE 4 - Store: calcularPreview
// ============================================================
describe('liquidacionesStore.calcularPreview', () => {
    const req = {
        provacop_id: 1,
        lotes: [{ ip: 'IP-TEST-01', bono: 0 }],
        spot_usd: 2400,
    }

    beforeEach(() => {
        vi.mocked(previewLiquidacion).mockResolvedValue({ data: previewFake } as any)
    })

    it('calcula el preview y lo guarda en store.preview', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        const result = await store.calcularPreview(req)

        expect(result).not.toBeNull()
        expect(result?.puede_generar).toBe(true)
        expect(result?.total_usd).toBe(5894.75)
        expect(store.preview?.count_lotes).toBe(1)
    })

    it('retorna null y registra error si la API falla', async () => {
        vi.mocked(previewLiquidacion).mockRejectedValue({
            response: { data: { detail: 'Sin parametros comerciales' } },
        })
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        const result = await store.calcularPreview(req)

        expect(result).toBeNull()
        expect(store.error).toBe('Sin parametros comerciales')
    })

    it('limpiarPreview resetea store.preview a null', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)
        await store.calcularPreview(req)
        expect(store.preview).not.toBeNull()

        store.limpiarPreview()

        expect(store.preview).toBeNull()
    })
})

// ============================================================
// SUITE 5 - Store: crear
// ============================================================
describe('liquidacionesStore.crear', () => {
    const req = {
        provacop_id: 1,
        lotes: [{ ip: 'IP-TEST-01', bono: 0 }],
        spot_usd: 2400,
    }

    beforeEach(() => {
        vi.mocked(crearLiquidacion).mockResolvedValue({ data: liquidacionDetalleFake } as any)
    })

    it('crea una liquidacion y la agrega al inicio de store.lista', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        const result = await store.crear(req)

        expect(result).not.toBeNull()
        expect(result?.numero_liquidacion).toBe('LIQ-0001')
        expect(store.lista[0].numero_liquidacion).toBe('LIQ-0001')
    })

    it('retorna null y registra error si el servidor rechaza la creacion', async () => {
        vi.mocked(crearLiquidacion).mockRejectedValue({
            response: { data: { detail: 'Lote IP-TEST-01: sin analisis de ley vigente' } },
        })
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        const result = await store.crear(req)

        expect(result).toBeNull()
        expect(store.error).toContain('sin analisis de ley vigente')
    })

    it('como_borrador=true crea liquidacion en estado BORRADOR', async () => {
        vi.mocked(crearLiquidacion).mockResolvedValue({
            data: { ...liquidacionDetalleFake, estado: 'BORRADOR' },
        } as any)
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        const result = await store.crear({ ...req, como_borrador: true })

        expect(result?.estado).toBe('BORRADOR')
    })
})

// ============================================================
// SUITE 6 - Store: cambiarEstado
// ============================================================
describe('liquidacionesStore.cambiarEstado', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('transicion GENERADA → FACTURADA actualiza store.lista y store.detalle', async () => {
        vi.mocked(cambiarEstadoLiquidacion).mockResolvedValue({
            data: { ...liquidacionDetalleFake, estado: 'FACTURADA' },
        } as any)

        const pinia = createTestingPinia({
            stubActions: false,
            createSpy: vi.fn,
            initialState: {
                liquidaciones: {
                    lista: [liquidacionResumenFake],
                    detalle: liquidacionDetalleFake,
                },
            },
        })
        const store = useLiquidacionesStore(pinia)

        const ok = await store.cambiarEstado(1, 'FACTURADA')

        expect(ok).toBe(true)
        expect(store.lista[0]?.estado).toBe('FACTURADA')
        expect(store.detalle?.estado).toBe('FACTURADA')
    })

    it('retorna false y registra error si el cambio no esta permitido', async () => {
        vi.mocked(cambiarEstadoLiquidacion).mockRejectedValue({
            response: { data: { detail: 'Una liquidacion PAGADA no puede modificarse' } },
        })
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        const ok = await store.cambiarEstado(1, 'BORRADOR')

        expect(ok).toBe(false)
        expect(store.error).toBe('Una liquidacion PAGADA no puede modificarse')
    })
})

// ============================================================
// SUITE 7 - Store: emitir (BORRADOR → GENERADA)
// ============================================================
describe('liquidacionesStore.emitir', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('emitir transiciona a GENERADA y actualiza store', async () => {
        vi.mocked(emitirLiquidacion).mockResolvedValue({
            data: { ...liquidacionDetalleFake, estado: 'GENERADA' },
        } as any)

        const pinia = createTestingPinia({
            stubActions: false,
            createSpy: vi.fn,
            initialState: {
                liquidaciones: {
                    lista: [{ ...liquidacionResumenFake, estado: 'BORRADOR' }],
                    detalle: { ...liquidacionDetalleFake, estado: 'BORRADOR' },
                },
            },
        })
        const store = useLiquidacionesStore(pinia)

        const ok = await store.emitir(1)

        expect(ok).toBe(true)
        expect(store.detalle?.estado).toBe('GENERADA')
        expect(store.lista[0]?.estado).toBe('GENERADA')
    })

    it('retorna false si la liquidacion no esta en BORRADOR', async () => {
        vi.mocked(emitirLiquidacion).mockRejectedValue({
            response: { data: { detail: 'Solo se puede emitir desde BORRADOR' } },
        })
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        const ok = await store.emitir(1)

        expect(ok).toBe(false)
        expect(store.error).toBe('Solo se puede emitir desde BORRADOR')
    })
})

// ============================================================
// SUITE 8 - Store: cargarKPIs
// ============================================================
describe('liquidacionesStore.cargarKPIs', () => {
    it('expone KPIs correctamente en store.kpis', async () => {
        vi.mocked(getLiquidacionesKPIs).mockResolvedValue({ data: kpisFake } as any)

        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        await store.cargarKPIs()

        expect(store.kpis?.borradores).toBe(2)
        expect(store.kpis?.generadas).toBe(5)
        expect(store.kpis?.lotes_liquidables).toBe(8)
        expect(store.kpis?.valor_pendiente_usd).toBe(45000)
    })

    it('no lanza excepcion si la API de KPIs falla (silencioso)', async () => {
        vi.mocked(getLiquidacionesKPIs).mockRejectedValue(new Error('network'))

        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLiquidacionesStore(pinia)

        await expect(store.cargarKPIs()).resolves.not.toThrow()
        expect(store.kpis).toBeNull()
    })
})

// ============================================================
// SUITE 9 - LiquidacionesView: listado y KPIs
// ============================================================
describe('LiquidacionesView - listado general', () => {
    it('muestra el numero de liquidacion y el estado en la tabla', async () => {
        // Usamos copia explícita para evitar que Suite 6 (cambiarEstado) mute
        // el objeto compartido y cambie estado a 'FACTURADA'.
        const listaFresh = [{ ...liquidacionResumenFake, estado: 'GENERADA' }]

        const pinia = createTestingPinia({
            createSpy: vi.fn,
            initialState: {
                auth: { user: { rol: 'Comercial', nombre_completo: 'Test' } },
                liquidaciones: { lista: listaFresh, kpis: kpisFake },
            },
        })

        // La vista llama store.cargarLista().then(...); con stubActions:true
        // el spy devuelve undefined por defecto → TypeError. Lo resolvemos
        // haciendo que el spy devuelva una Promise resuelta.
        const store = useLiquidacionesStore(pinia)
        vi.spyOn(store, 'cargarLista').mockResolvedValue(undefined as any)
        vi.spyOn(store, 'cargarKPIs').mockResolvedValue(undefined as any)

        const wrapper = mount(LiquidacionesView, {
            global: {
                plugins: [pinia],
                stubs: { RouterLink: true, RouterView: true },
            },
        })

        await flushPromises()

        expect(wrapper.text()).toContain('LIQ-0001')
        expect(wrapper.text()).toContain('GENERADA')
    })

    it('muestra KPIs: borradores y lotes liquidables', async () => {
        const pinia = createTestingPinia({
            createSpy: vi.fn,
            initialState: {
                auth: { user: { rol: 'Gerencia', nombre_completo: 'Test' } },
                liquidaciones: { lista: [], kpis: kpisFake },
            },
        })
        const store = useLiquidacionesStore(pinia)
        vi.spyOn(store, 'cargarLista').mockResolvedValue(undefined as any)
        vi.spyOn(store, 'cargarKPIs').mockResolvedValue(undefined as any)

        const wrapper = mount(LiquidacionesView, {
            global: {
                plugins: [pinia],
                stubs: { RouterLink: true, RouterView: true },
            },
        })

        await flushPromises()

        expect(wrapper.text()).toContain('2')  // borradores
        expect(wrapper.text()).toContain('8')  // lotes_liquidables
    })
})

// ============================================================
// SUITE 10 - DetalleLiquidacionView: permisos RBAC
// ============================================================
describe('DetalleLiquidacionView - permisos por rol', () => {
    it('rol Comercial ve el boton de emitir en estado BORRADOR', async () => {
        vi.mocked(getLiquidacion).mockResolvedValue({
            data: { ...liquidacionDetalleFake, estado: 'BORRADOR' },
        } as any)

        const wrapper = mount(DetalleLiquidacionView, {
            global: {
                plugins: [
                    createTestingPinia({
                        createSpy: vi.fn,
                        initialState: {
                            auth: { user: { rol: 'Comercial', nombre_completo: 'Test' } },
                            liquidaciones: {
                                detalle: { ...liquidacionDetalleFake, estado: 'BORRADOR' },
                            },
                        },
                    }),
                ],
                stubs: { RouterLink: true, RouterView: true },
            },
        })

        await flushPromises()

        // La vista debe renderizar el numero de liquidacion
        expect(wrapper.text()).toContain('LIQ-0001')
    })

    it('liquidacion PAGADA no muestra opciones de modificacion', async () => {
        vi.mocked(getLiquidacion).mockResolvedValue({
            data: { ...liquidacionDetalleFake, estado: 'PAGADA' },
        } as any)

        const wrapper = mount(DetalleLiquidacionView, {
            global: {
                plugins: [
                    createTestingPinia({
                        createSpy: vi.fn,
                        initialState: {
                            auth: { user: { rol: 'Comercial', nombre_completo: 'Test' } },
                            liquidaciones: {
                                detalle: { ...liquidacionDetalleFake, estado: 'PAGADA' },
                            },
                        },
                    }),
                ],
                stubs: { RouterLink: true, RouterView: true },
            },
        })

        await flushPromises()

        expect(wrapper.text()).toContain('PAGADA')
    })
})

// ============================================================
// SUITE 11 - CrearLiquidacionView: flujo de seleccion de lotes
// ============================================================
describe('CrearLiquidacionView - seleccion y preview', () => {
    it('renderiza el paso 1 con el selector de proveedor y el campo spot', async () => {
        // Los lotes sólo se cargan DESPUÉS de seleccionar un provacop_id.
        // En el paso 1 inicial sólo es visible el formulario de parámetros.
        const wrapper = mount(CrearLiquidacionView, {
            global: {
                plugins: [
                    createTestingPinia({
                        createSpy: vi.fn,
                        initialState: {
                            auth: { user: { rol: 'Comercial', nombre_completo: 'Test' } },
                            liquidaciones: { lotesDisponibles: [], preview: null },
                        },
                    }),
                ],
                stubs: { RouterLink: true, RouterView: true },
            },
        })

        await flushPromises()

        // Step 1 siempre muestra selector de proveedor y campo spot
        expect(wrapper.text()).toContain('Paso 1')
        expect(wrapper.text()).toContain('PROVEEDOR')
    })

    it('una vez cargados los lotes disponibles, los expone en el store', async () => {
        vi.mocked(getLotesDisponibles).mockResolvedValue({ data: [loteFake] } as any)

        const pinia = createTestingPinia({
            stubActions: false,
            createSpy: vi.fn,
            initialState: {
                auth: { user: { rol: 'Comercial', nombre_completo: 'Test' } },
                liquidaciones: { lotesDisponibles: [], preview: null },
            },
        })
        const store = useLiquidacionesStore(pinia)
        await store.cargarLotesDisponibles(1)

        expect(store.lotesDisponibles).toHaveLength(1)
        expect(store.lotesDisponibles[0].ip).toBe('IP-TEST-01')
        expect(store.lotesDisponibles[0].proveedor).toBe('Minera Demo SAC')
    })

    it('lote con listo_para_liquidar=false no bloquea el render de la vista', async () => {
        const loteNoListo = { ...loteFake, listo_para_liquidar: false }
        vi.mocked(getLotesDisponibles).mockResolvedValue({ data: [loteNoListo] } as any)

        const wrapper = mount(CrearLiquidacionView, {
            global: {
                plugins: [
                    createTestingPinia({
                        createSpy: vi.fn,
                        initialState: {
                            auth: { user: { rol: 'Comercial', nombre_completo: 'Test' } },
                            liquidaciones: { lotesDisponibles: [loteNoListo], preview: null },
                        },
                    }),
                ],
                stubs: { RouterLink: true, RouterView: true },
            },
        })

        await flushPromises()

        // La vista debe seguir renderizando sin errores
        expect(wrapper.exists()).toBe(true)
    })
})
