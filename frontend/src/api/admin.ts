import api from './axios'

export interface ConstanteCalculo {
    clave: string
    valor: string
    default: string
    descripcion: string
    en_bd: boolean
}

export interface ConstanteUpdate {
    valor: string
}

export const adminApi = {
    getConstantesCalculo: (): Promise<ConstanteCalculo[]> =>
        api.get<ConstanteCalculo[]>('/admin/config-calculo').then(r => r.data),

    updateConstante: (clave: string, valor: string): Promise<ConstanteCalculo> =>
        api.put<ConstanteCalculo>(`/admin/config-calculo/${clave}`, { valor }).then(r => r.data),
}
