/**
 * useBalanza.ts
 * Composable que gestiona la conexión WebSocket con el agente local de balanza.
 *
 * Uso en RegistrarCamion.vue:
 *   const { peso, pesoDisplay, estable, conectado, error, capturar } = useBalanza()
 */

import { ref, onMounted, onUnmounted } from 'vue'

// Dirección del agente local - en producción siempre es localhost
// (el agente corre en la misma PC que el operador)
const WS_URL = import.meta.env.VITE_BALANZA_WS_URL ?? 'ws://localhost:8765'

// ── Tipos ──────────────────────────────────────────────────

export interface BalanzaConfig {
    puerto: string
    baudrate: number
    decimal_places: number
}

export interface BalanzaState {
    peso: number | null           // kg, float
    pesoDisplay: string           // ej: "12.500"
    unidad: string                // "KG"
    estable: boolean
    conectado: boolean            // puerto serial OK
    wsConectado: boolean          // WebSocket al agente OK
    error: string | null
    config: BalanzaConfig | null
}

// ── Composable ─────────────────────────────────────────────

export function useBalanza() {
    const peso = ref<number | null>(null)
    const pesoDisplay = ref<string>('-')
    const unidad = ref<string>('KG')
    const estable = ref<boolean>(false)
    const conectado = ref<boolean>(false)   // serial
    const wsConectado = ref<boolean>(false)   // websocket
    const error = ref<string | null>(null)
    const config = ref<BalanzaConfig | null>(null)

    let ws: WebSocket | null = null
    let reconectarTimer: ReturnType<typeof setTimeout> | null = null
    let destroyed = false

    // ── Conexión ─────────────────────────────────────────────

    function conectar() {
        if (destroyed) return

        try {
            ws = new WebSocket(WS_URL)
        } catch {
            scheduleReconexion()
            return
        }

        ws.onopen = () => {
            wsConectado.value = true
            error.value = null
            // Pedir estado inicial explícitamente
            ws?.send(JSON.stringify({ tipo: 'status' }))
        }

        ws.onmessage = (event: MessageEvent) => {
            try {
                const msg = JSON.parse(event.data as string)
                procesarMensaje(msg)
            } catch {
                // ignorar mensajes mal formados
            }
        }

        ws.onerror = () => {
            wsConectado.value = false
            error.value = 'No se pudo conectar con el agente de balanza.'
        }

        ws.onclose = () => {
            wsConectado.value = false
            conectado.value = false
            if (!destroyed) scheduleReconexion()
        }
    }

    function scheduleReconexion() {
        if (destroyed) return
        reconectarTimer = setTimeout(() => {
            if (!destroyed) conectar()
        }, 3000)
    }

    // ── Procesar mensajes entrantes ───────────────────────────

    function procesarMensaje(msg: Record<string, unknown>) {
        switch (msg.tipo) {
            case 'peso':
            case 'estado_inicial':
                peso.value = (msg.peso as number) ?? null
                pesoDisplay.value = (msg.peso_display as string) ?? '-'
                unidad.value = (msg.unidad as string) ?? 'KG'
                estable.value = (msg.estable as boolean) ?? false
                conectado.value = (msg.conectado as boolean) ?? false
                if (msg.config) config.value = msg.config as BalanzaConfig
                break

            case 'captura':
                // El frontend solicitó captura puntual - emitir evento
                _capturaResolver?.({
                    peso: (msg.peso as number) ?? null,
                    pesoDisplay: (msg.peso_display as string) ?? '-',
                    estable: (msg.estable as boolean) ?? false,
                })
                _capturaResolver = null
                break

            case 'error':
                conectado.value = false
                error.value = (msg.mensaje as string) ?? 'Error desconocido en balanza.'
                break

            case 'pong':
                // heartbeat OK - no hacer nada
                break
        }
    }

    // ── Captura puntual (Promise) ─────────────────────────────
    // Permite hacer: const lectura = await capturar()

    type CapturaResult = { peso: number | null; pesoDisplay: string; estable: boolean }
    let _capturaResolver: ((v: CapturaResult) => void) | null = null

    async function capturar(): Promise<CapturaResult> {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            // Fallback: devolver el último valor conocido sin esperar
            return { peso: peso.value, pesoDisplay: pesoDisplay.value, estable: estable.value }
        }

        return new Promise((resolve) => {
            _capturaResolver = resolve
            ws!.send(JSON.stringify({ tipo: 'capturar' }))
            // Timeout de seguridad: si el agente no responde en 2s, usar último valor
            setTimeout(() => {
                if (_capturaResolver) {
                    _capturaResolver({ peso: peso.value, pesoDisplay: pesoDisplay.value, estable: estable.value })
                    _capturaResolver = null
                }
            }, 2000)
        })
    }

    // ── Lifecycle ─────────────────────────────────────────────

    onMounted(() => {
        conectar()
    })

    onUnmounted(() => {
        destroyed = true
        if (reconectarTimer) clearTimeout(reconectarTimer)
        ws?.close()
    })

    return {
        peso,
        pesoDisplay,
        unidad,
        estable,
        conectado,
        wsConectado,
        error,
        config,
        capturar,
    }
}
