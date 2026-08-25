import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginView from '@/views/auth/LoginView.vue'
import BalanzaView from '@/views/balanza/BalanzaView.vue'
import RegistrarCamionView from '@/views/balanza/RegistrarCamionView.vue'
import SesionView from '@/views/balanza/SesionView.vue'
import MuestreoView from '@/views/muestreo/MuestreoView.vue'
import PruebasView from '@/views/pruebas/PruebasView.vue'
import RegistrarPruebasView from '@/views/pruebas/RegistrarPruebasView.vue'
import RecuperacionesPruebasView from '@/views/pruebas/RecuperacionesView.vue'
import LaboratorioView from '@/views/laboratorio/LaboratorioDashboardView.vue'
import RegistrarLeyView from '@/views/laboratorio/RegistrarLeyView.vue'
import RegistrarRecuperacionView from '@/views/laboratorio/RegistrarRecuperacionView.vue'
import RegistrarSolidosView from '@/views/laboratorio/RegistrarSolidosView.vue'
import RegistrarSolucionView from '@/views/laboratorio/RegistrarSolucionView.vue'
import DetalleLoteView from '@/views/laboratorio/DetalleLoteView.vue'
import UnauthorizedView from '@/views/auth/UnauthorizedView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'
import MainLayout from '@/layouts/MainLayout.vue'
import RegistrarHumedadView from '@/views/muestreo/RegistrarHumedadView.vue'
import ImportarCertificadoLeyView from '@/views/laboratorio/ImportarCertificadoLeyView.vue'
import ImportarCertificadoRecuperacionView from '@/views/laboratorio/ImportarCertificadoRecView.vue'
import LiquidacionesView from '@/views/liquidaciones/LiquidacionesView.vue'
import CrearLiquidacionView from '@/views/liquidaciones/CrearLiquidacionView.vue'
import DetalleLiquidacionView from '@/views/liquidaciones/DetalleLiquidacionView.vue'
import SpotHistoricoView from '@/views/liquidaciones/SpotHistoricoView.vue'
import TercerosView from '@/views/terceros/TercerosView.vue'
import RumasView from '@/views/rumas/RumasView.vue'
import DetalleRumaView from '@/views/rumas/DetalleRumaView.vue'
import CampanasView from '@/views/rumas/CampanasView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ── Ruta Pública ──
    { path: '/login', name: 'Login', component: LoginView },

    // ── Rutas Protegidas (Con Menú Lateral) ──
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        // Dashboard principal
        { path: 'dashboard', name: 'Dashboard', component: DashboardView, meta: { permiso: { modulo: 'DASHBOARD', operacion: 'VIEW' } } },

        // Balanza
        { path: 'balanza', name: 'Balanza', component: BalanzaView, meta: { permiso: { modulo: 'BALANZA', operacion: 'VIEW' } } },
        { path: 'balanza/nueva', name: 'RegistrarCamion', component: RegistrarCamionView, meta: { permiso: { modulo: 'BALANZA', operacion: 'VIEW' } } },
        { path: 'balanza/:id', name: 'SesionBalanza', component: SesionView, meta: { permiso: { modulo: 'BALANZA', operacion: 'VIEW' } } },

        // Muestreo
        { path: 'muestreo', name: 'Muestreo', component: MuestreoView, meta: { permiso: { modulo: 'MUESTREO', operacion: 'VIEW' } } },
        { path: 'muestreo/:ip', name: 'RegistrarHumedad', component: RegistrarHumedadView, meta: { permiso: { modulo: 'MUESTREO', operacion: 'VIEW' } } },

        // Pruebas
        { path: 'pruebas', name: 'Pruebas', component: PruebasView, meta: { permiso: { modulo: 'PRUEBAS_MET', operacion: 'VIEW' } } },
        { path: 'pruebas/recuperaciones', name: 'Recuperaciones', component: RecuperacionesPruebasView, meta: { permiso: { modulo: 'PRUEBAS_MET', operacion: 'VIEW' } } },
        { path: 'pruebas/:ip', name: 'RegistrarPrueba', component: RegistrarPruebasView, meta: { permiso: { modulo: 'PRUEBAS_MET', operacion: 'VIEW' } } },

        // Laboratorio
        { path: 'laboratorio', name: 'Laboratorio', component: LaboratorioView, meta: { permiso: { modulo: 'LABORATORIO', operacion: 'VIEW' } } },
        { path: 'laboratorio/ley/:cip', name: 'RegistrarLey', component: RegistrarLeyView, meta: { permiso: { modulo: 'LABORATORIO', operacion: 'VIEW' } } },
        { path: 'laboratorio/recuperacion/:cip', name: 'RegistrarRecuperacion', component: RegistrarRecuperacionView, meta: { permiso: { modulo: 'LABORATORIO', operacion: 'VIEW' } } },
        { path: 'laboratorio/solidos/:cip', name: 'RegistrarSolidos', component: RegistrarSolidosView, meta: { permiso: { modulo: 'LABORATORIO', operacion: 'VIEW' } } },
        { path: 'laboratorio/solucion/:cip', name: 'RegistrarSolucion', component: RegistrarSolucionView, meta: { permiso: { modulo: 'LABORATORIO', operacion: 'VIEW' } } },
        { path: 'laboratorio/lote/:ip', name: 'DetalleLote', component: DetalleLoteView, meta: { permiso: { modulo: 'LABORATORIO', operacion: 'VIEW' } } },
        { path: 'laboratorio/importar-ley/:cip', name: 'ImportarCertLey', component: ImportarCertificadoLeyView, meta: { permiso: { modulo: 'LABORATORIO', operacion: 'VIEW' } } },
        { path: 'laboratorio/importar-rec/:cip', name: 'ImportarCertRec', component: ImportarCertificadoRecuperacionView, meta: { permiso: { modulo: 'LABORATORIO', operacion: 'VIEW' } } },

        // Liquidaciones
        { path: 'liquidaciones', name: 'Liquidaciones', component: LiquidacionesView, meta: { permiso: { modulo: 'LIQUIDACIONES', operacion: 'VIEW' } } },
        { path: 'liquidaciones/nueva', name: 'CrearLiquidacion', component: CrearLiquidacionView, meta: { permiso: { modulo: 'LIQUIDACIONES', operacion: 'CREATE' } } },
        { path: 'liquidaciones/spots', name: 'SpotHistorico', component: SpotHistoricoView, meta: { permiso: { modulo: 'LIQUIDACIONES', operacion: 'VIEW' } } },
        { path: 'liquidaciones/:id', name: 'DetalleLiquidacion', component: DetalleLiquidacionView, meta: { permiso: { modulo: 'LIQUIDACIONES', operacion: 'VIEW' } } },

        // Gestión
        { path: 'terceros', name: 'Terceros', component: TercerosView, meta: { permiso: { modulo: 'TERCEROS', operacion: 'VIEW' } } },

        // Rumas
        { path: 'rumas', name: 'Rumas', component: RumasView, meta: { permiso: { modulo: 'RUMAS', operacion: 'VIEW' } } },
        { path: 'rumas/:id', name: 'DetalleRuma', component: DetalleRumaView, meta: { permiso: { modulo: 'RUMAS', operacion: 'VIEW' } } },
        { path: 'administracion/campanas', name: 'Campanas', component: CampanasView, meta: { permiso: { modulo: 'CAMPANAS', operacion: 'CREATE' } } },

        // Administración (vista unificada con tabs: Usuarios / Parámetros / Notificaciones)
        { path: 'administracion', name: 'Administracion', component: () => import('@/views/admin/AdminView.vue'), meta: { permiso: { modulo: 'ADMINISTRACION', operacion: 'VIEW' } } },
        { path: 'administracion/config', redirect: { name: 'Administracion' } },

        // Error
        { path: 'unauthorized', name: 'Unauthorized', component: UnauthorizedView },

        // Redirección dinámica según rol al entrar a la raíz "/"
        {
          path: '',
          redirect: () => {
            const auth = useAuthStore()
            if (!auth.accessToken) return '/login'

            const rol = auth.user?.rol
            switch (rol) {
              case 'Admin':
              case 'Gerencia':
              case 'JefeComercial':
              case 'Comercial':
                return '/dashboard'
              case 'OperadorBalanza':
                return '/balanza'
              case 'TecnicoMuestreo':    // sin acento — coincide con backend
                return '/muestreo'
              case 'Laboratorista':
                return '/laboratorio'
              case 'Metalurgista':
                return '/pruebas'
              default:
                return '/login'
            }
          }
        }
      ]
    },

    // ── Comodín para 404 ──
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

// ── Guard de autenticación ──
router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Si la ruta requiere auth y no hay token
  if (to.meta.requiresAuth && !auth.accessToken) {
    return { name: 'Login' }
  }

  // Si hay token pero no hay datos de usuario (ej. refresh F5), los cargamos
  if (auth.accessToken && !auth.user && to.name !== 'Login') {
    try {
      await auth.fetchMe()
    } catch {
      auth.clearTokens()
      return { name: 'Login' }
    }
  }

  // Guard por permisos RBAC de ruta (meta.permiso)
  if (to.meta.permiso) {
    const p = to.meta.permiso as { modulo: string; operacion: string }
    if (!auth.puede(p.modulo, p.operacion)) return { name: 'Unauthorized' }
  }



  return true
})

export default router
