/**
 * usePermiso — Composable para verificar permisos RBAC en componentes Vue.
 *
 * Uso:
 *   const { puede } = usePermiso()
 *   const puedeCrearLote = computed(() => puede('BALANZA', 'CREATE'))
 *   const esConfidencial = computed(() => puede('LABORATORIO', 'VIEW_CONFIDENTIAL'))
 *
 * Operaciones disponibles: VIEW, CREATE, UPDATE, DELETE, VIEW_CONFIDENTIAL, EDIT_PARAMS
 * Modulos disponibles: BALANZA, MUESTREO, LABORATORIO, PRUEBAS_MET, RUMAS,
 *                      LIQUIDACIONES, CAMPANAS, TERCEROS, DASHBOARD, ADMINISTRACION
 */
import { useAuthStore } from '@/stores/auth'

export function usePermiso() {
  const auth = useAuthStore()

  /**
   * Verifica si el usuario actual tiene el permiso indicado.
   * Reactivo: se actualiza automaticamente si cambia el estado del store.
   *
   * @param modulo    - Codigo del modulo (ej: 'BALANZA', 'LABORATORIO')
   * @param operacion - Codigo de la operacion (ej: 'VIEW', 'CREATE', 'EDIT_PARAMS')
   */
  function puede(modulo: string, operacion: string): boolean {
    return auth.puede(modulo, operacion)
  }

  return { puede }
}
