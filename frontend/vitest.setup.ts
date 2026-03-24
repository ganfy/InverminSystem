import 'fake-indexeddb/auto'
import { vi } from 'vitest'

// 1. Mock global de la API para evitar llamadas reales de red
vi.mock('@/api/balanza', () => ({
    balanzaApi: {
        reservarBloqueIP: vi.fn(),
        reservarBloqueTK: vi.fn(),
        obtenerCacheProvacops: vi.fn(),
        listarSesiones: vi.fn(),
        obtenerSesion: vi.fn(),
        crearSesion: vi.fn(),
        editarSesion: vi.fn(),
        finalizarSesion: vi.fn(),
        pausarSesion: vi.fn(),
        reanudarSesion: vi.fn(),
        agregarLote: vi.fn(),
        editarLote: vi.fn(),
        eliminarLote: vi.fn(),
        syncBatch: vi.fn(),
    }
}))

// 2. Mock global del UI Store para evitar errores de renderizado de notificaciones
vi.mock('@/stores/ui', () => ({
    useUiStore: vi.fn(() => ({
        toast: vi.fn(),
        showConfirm: vi.fn(),
    }))
}))
