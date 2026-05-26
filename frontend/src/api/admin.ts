import api from './axios'

export interface ConstanteCalculo {
    clave: string
    valor: string
    default: string
    descripcion: string
    en_bd: boolean
}

export interface TelegramConfig {
    bot_token: string
    chat_id: string
    intervalo_min: number
    configurado: boolean
}

export interface TelegramConfigUpdate {
    bot_token: string
    chat_id: string
    intervalo_min: number
}

export const adminApi = {
    // ── Constantes de cálculo ──────────────────────────────────────────────
    getConstantesCalculo: (): Promise<ConstanteCalculo[]> =>
        api.get<ConstanteCalculo[]>('/admin/config-calculo').then(r => r.data),

    updateConstante: (clave: string, valor: string): Promise<ConstanteCalculo> =>
        api.put<ConstanteCalculo>(`/admin/config-calculo/${clave}`, { valor }).then(r => r.data),

    // ── Telegram ───────────────────────────────────────────────────────────
    getTelegramConfig: (): Promise<TelegramConfig> =>
        api.get<TelegramConfig>('/admin/telegram').then(r => r.data),

    updateTelegramConfig: (payload: TelegramConfigUpdate): Promise<TelegramConfig> =>
        api.put<TelegramConfig>('/admin/telegram', payload).then(r => r.data),

    testTelegram: (): Promise<{ mensaje: string }> =>
        api.post<{ mensaje: string }>('/admin/telegram/test').then(r => r.data),
}
