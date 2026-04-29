import { mount, flushPromises } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createTestingPinia } from '@pinia/testing'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { laboratorioApi } from '@/api/laboratorio'
import LaboratorioDashboardView from '@/views/laboratorio/LaboratorioDashboardView.vue'
import { obtenerCipsLabCache, encolarAnalisisLey, encolarAnalisisRecuperacion } from '@/composables/useOfflineQueue'
import { useSync } from '@/composables/useSync'
import { useUiStore } from '@/stores/ui'

// -- Mocks globales --
vi.mock('@/api/laboratorio', () => ({
    laboratorioApi: {
        listarCips: vi.fn(),
        listarLotes: vi.fn(),
        registrarLey: vi.fn(),
        descartarLey: vi.fn(),
        subirCertificadoLey: vi.fn(),
        getLeyComercial: vi.fn(),
        completarRecuperacion: vi.fn(),
        registrarRecuperacion: vi.fn(),
        descartarRecuperacion: vi.fn(),
        extraerCertificadoLey: vi.fn(),
        extraerCertificadoRecuperacion: vi.fn(),
        generarCertificadoLeyInterno: vi.fn(),
        generarCertificadoRecInterno: vi.fn(),
        eliminarLey: vi.fn(),
        eliminarRecuperacion: vi.fn(),
        enviarRecuperacion: vi.fn(),
        detalleLote: vi.fn(),
        subirCertificadoRecuperacion: vi.fn(),
    },
}))

vi.mock('@/composables/useSync', () => ({
    useSync: vi.fn(() => ({ online: { value: true } })),
}))

vi.mock('@/composables/useOfflineQueue', () => ({
    encolarAnalisisLey: vi.fn(),
    encolarAnalisisRecuperacion: vi.fn(),
    guardarCipsLabCache: vi.fn(),
    obtenerCipsLabCache: vi.fn().mockResolvedValue([]),
}))

vi.mock('vue-router', async (importOriginal) => {
    const actual = await importOriginal<typeof import('vue-router')>()
    return {
        ...actual,
        useRouter: vi.fn(() => ({ push: vi.fn() })),
        useRoute: vi.fn(() => ({ params: { ip: 'IP-0001', cip: 'CIP-000001-A1' } })),
    }
})

vi.mock('@/stores/ui', () => ({
    useUiStore: vi.fn(() => ({
        showConfirm: vi.fn().mockResolvedValue(true),
        toast: vi.fn(),
    })),
}))

// -- Fixtures --
const cipFake = {
    cip: 'CIP-000001-A1',
    ip: null,
    laboratorio: 'Lab Externo A',
    tipo_muestra: 'Laboratorio',
    estado_ley: 'PENDIENTE',
    estado_recuperacion: 'PENDIENTE',
    material: 'Au',
    analisis_ley: [],
    analisis_recuperacion: [],
    prueba_metalurgica: null,
    estado_muestra: 'PENDIENTE',
}

const loteFake = {
    ip: 'IP-0001',
    proveedor: 'Proveedor Demo',
    acopiador: null,
    tmh: 10,
    tms: 9.5,
    ley_planta: 0.45,
    ley_minero: null,
    analisis_ley: [],
    analisis_recuperacion: [],
    estado: 'RECEPCIONADO',
    tiene_dirimencia: false,
}

// ============================================================
// SUITE 1 - Store: cargarCips (online)
// ============================================================
describe('laboratorioStore.cargarCips - online', () => {
    beforeEach(() => {
        vi.mocked(laboratorioApi.listarCips).mockResolvedValue([cipFake as any])
    })

    it('carga CIPs desde la API y los expone en store.cips', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLaboratorioStore(pinia)
        await store.cargarCips()
        expect(store.cips).toHaveLength(1)
        expect(store.cips[0].cip).toBe('CIP-000001-A1')
    })
})

// ============================================================
// SUITE 2 - Store: cargarCips (offline - fallback a cache)
// ============================================================
describe('laboratorioStore.cargarCips - offline fallback', () => {
    beforeEach(() => {
        vi.mocked(laboratorioApi.listarCips).mockRejectedValue(new Error('network'))
        vi.mocked(obtenerCipsLabCache).mockResolvedValue([cipFake])
    })

    it('usa la cache cuando la API falla', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLaboratorioStore(pinia)
        await store.cargarCips()
        expect(store.cips).toHaveLength(1)
    })
})

// ============================================================
// SUITE 3 - Store: registrarLey (online)
// ============================================================
describe('laboratorioStore.registrarLey - online', () => {
    const payload = {
        cip: 'CIP-000001-A1',
        laboratorio: 'Lab Externo A',
        tipo_analisis: 'externo',
        material: 'Au',
        ley_fino: 0.20,
        ley_grueso: 0.25,
        origen_datos: 'manual',
        fecha_analisis: '2026-01-15',
    }

    beforeEach(() => {
        vi.mocked(useSync).mockReturnValue({ online: { value: true } } as any)
        vi.mocked(laboratorioApi.registrarLey).mockResolvedValue({ id: 1, ...payload } as any)
    })

    it('llama a la API y retorna el análisis creado', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLaboratorioStore(pinia)
        const resultado = await store.registrarLey(payload)
        expect(laboratorioApi.registrarLey).toHaveBeenCalledWith(payload)
        expect(resultado?.id).toBe(1)
    })

    it('sube certificado si se provee un archivo', async () => {
        vi.mocked(laboratorioApi.subirCertificadoLey).mockResolvedValue({ certificado_url: '/cert.pdf' })
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLaboratorioStore(pinia)
        const archivo = new File(['pdf'], 'cert.pdf', { type: 'application/pdf' })
        await store.registrarLey(payload, archivo)
        expect(laboratorioApi.subirCertificadoLey).toHaveBeenCalledWith(1, archivo)
    })
})

// ============================================================
// SUITE 4 - Store: registrarLey (offline - encola)
// ============================================================
describe('laboratorioStore.registrarLey - offline', () => {
    beforeEach(() => {
        vi.mocked(useSync).mockReturnValue({ online: { value: false } } as any)
    })

    afterEach(() => {
        // Restaurar estado online para que no afecte a otros tests
        vi.mocked(useSync).mockReturnValue({ online: { value: true } } as any)
    })

    it('encola el análisis en IndexedDB cuando no hay conexion', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const ui = useUiStore(pinia)
        ui.toast = vi.fn() as any

        vi.mocked(ui.toast).mockReturnValue(undefined as any)

        const store = useLaboratorioStore(pinia)
        const payload = {
            cip: 'CIP-000001-A1', laboratorio: 'Lab', tipo_analisis: 'externo',
            material: 'Au', ley_fino: 0.2, ley_grueso: 0.25,
            origen_datos: 'manual', fecha_analisis: '2026-01-15',
        }
        await store.registrarLey(payload)
        expect(encolarAnalisisLey).toHaveBeenCalled()
    })
})

// ============================================================
// SUITE 5 - Store: descartarLey
// ============================================================
describe('laboratorioStore.descartarLey', () => {
    beforeEach(() => {
        // Limpiamos el historial de llamadas antes de cada test
        // para que no se filtren datos ("Fuera de rango") al siguiente.
        vi.clearAllMocks()
    })

    it('llama a la API de descartar y retorna true', async () => {
        vi.mocked(laboratorioApi.descartarLey).mockResolvedValue({ id: 1 } as any)
        vi.mocked(useUiStore).mockReturnValue({
            showConfirm: vi.fn().mockResolvedValue(true),
            toast: vi.fn(),
        } as any)

        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLaboratorioStore(pinia)
        const ok = await store.descartarLey(1, 'Fuera de rango')

        expect(ok).toBe(true)
        expect(laboratorioApi.descartarLey).toHaveBeenCalledWith(1, { justificacion: 'Fuera de rango' })
    })

    it('cancela si el usuario no confirma', async () => {
        vi.mocked(useUiStore).mockReturnValue({
            showConfirm: vi.fn().mockResolvedValue(false),
            toast: vi.fn(),
        } as any)

        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
        const store = useLaboratorioStore(pinia)
        const ok = await store.descartarLey(1, 'Test')

        expect(ok).toBe(false)
        expect(laboratorioApi.descartarLey).not.toHaveBeenCalled()
    })
})

// ============================================================
// SUITE 6 - Store: completarRecuperacion (offline)
// ============================================================
describe('laboratorioStore.completarRecuperacion - offline', () => {
    beforeEach(() => {
        vi.mocked(useSync).mockReturnValue({ online: { value: false } } as any)
    })

    afterEach(() => {
        vi.mocked(useSync).mockReturnValue({ online: { value: true } } as any)
    })

    it('encola la recuperacion cuando no hay conexion', async () => {
        const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })

        vi.mocked(useUiStore).mockReturnValue({
            toast: vi.fn(),
        } as any)

        const store = useLaboratorioStore(pinia)
        await store.completarRecuperacion(5, { ley_cola: 0.02, ley_liquido: 0.01, fecha_analisis: '2026-01-20' })
        expect(encolarAnalisisRecuperacion).toHaveBeenCalled()
    })
})

// ============================================================
// SUITE 7 - LaboratorioDashboard: vista Laboratorista (solo CIPs)
// ============================================================
describe('LaboratorioDashboardView - rol Laboratorista', () => {
    it('muestra la lista de CIPs y no expone IPs', async () => {
        vi.mocked(laboratorioApi.listarCips).mockResolvedValue([cipFake as any])
        vi.mocked(laboratorioApi.listarLotes).mockResolvedValue([])

        const wrapper = mount(LaboratorioDashboardView, {
            global: {
                plugins: [
                    createTestingPinia({
                        createSpy: vi.fn,
                        initialState: {
                            auth: { user: { rol: 'Laboratorista', nombre_completo: 'Lab User' } },
                            laboratorio: { cips: [cipFake], lotes: [] },
                        },
                    }),
                ],
                stubs: { RouterLink: true, RouterView: true },
            },
        })

        await flushPromises()
        // El CIP debe aparecer en pantalla
        expect(wrapper.text()).toContain('CIP-000001-A1')
        // El IP real NO debe aparecer (confidencialidad)
        expect(wrapper.text()).not.toContain('IP-0001')
    })
})

// ============================================================
// SUITE 8 - LaboratorioDashboard: vista Comercial (ve IPs)
// ============================================================
describe('LaboratorioDashboardView - rol Comercial', () => {
    it('muestra IPs ademas de CIPs', async () => {
        const cipConIp = { ...cipFake, ip: 'IP-0001' }
        vi.mocked(laboratorioApi.listarLotes).mockResolvedValue([loteFake as any])

        const wrapper = mount(LaboratorioDashboardView, {
            global: {
                plugins: [
                    createTestingPinia({
                        createSpy: vi.fn,
                        initialState: {
                            auth: { user: { rol: 'Comercial', nombre_completo: 'Comercial User' } },
                            laboratorio: { cips: [cipConIp], lotes: [loteFake] },
                        },
                    }),
                ],
                stubs: { RouterLink: true, RouterView: true },
            },
        })

        await flushPromises()
        expect(wrapper.text()).toContain('IP-0001')
    })
})
