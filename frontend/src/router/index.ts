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
        { path: 'dashboard', name: 'Dashboard', component: DashboardView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial'] } },

        // Balanza
        { path: 'balanza', name: 'Balanza', component: BalanzaView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'OperadorBalanza'] } },
        { path: 'balanza/nueva', name: 'RegistrarCamion', component: RegistrarCamionView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'OperadorBalanza'] } },
        { path: 'balanza/:id', name: 'SesionBalanza', component: SesionView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'OperadorBalanza'] } },

        // Muestreo
        { path: 'muestreo', name: 'Muestreo', component: MuestreoView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'TecnicoMuestreo'] } },
        { path: 'muestreo/:ip', name: 'RegistrarHumedad', component: RegistrarHumedadView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'TecnicoMuestreo'] } },

        // Pruebas
        { path: 'pruebas', name: 'Pruebas', component: PruebasView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'Metalurgista'] } },
        { path: 'pruebas/recuperaciones', name: 'Recuperaciones', component: RecuperacionesPruebasView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'Metalurgista'] } },
        { path: 'pruebas/:ip', name: 'RegistrarPrueba', component: RegistrarPruebasView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'Metalurgista'] } },

        // Laboratorio
        { path: 'laboratorio', name: 'Laboratorio', component: LaboratorioView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'Laboratorista'] } },
        { path: 'laboratorio/ley/:cip', name: 'RegistrarLey', component: RegistrarLeyView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'Laboratorista'] } },
        { path: 'laboratorio/recuperacion/:cip', name: 'RegistrarRecuperacion', component: RegistrarRecuperacionView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'Laboratorista'] } },
        { path: 'laboratorio/solidos/:cip', name: 'RegistrarSolidos', component: RegistrarSolidosView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'Laboratorista'] } },
        { path: 'laboratorio/solucion/:cip', name: 'RegistrarSolucion', component: RegistrarSolucionView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'Laboratorista'] } },
        { path: 'laboratorio/lote/:ip', name: 'DetalleLote', component: DetalleLoteView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial'] } },
        { path: 'laboratorio/importar-ley/:cip', name: 'ImportarCertLey', component: ImportarCertificadoLeyView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'Laboratorista'] } },
        { path: 'laboratorio/importar-rec/:cip', name: 'ImportarCertRec', component: ImportarCertificadoRecuperacionView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial', 'Laboratorista'] } },

        // Liquidaciones
        { path: 'liquidaciones', name: 'Liquidaciones', component: LiquidacionesView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial'] } },
        { path: 'liquidaciones/nueva', name: 'CrearLiquidacion', component: CrearLiquidacionView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial'] } },
        { path: 'liquidaciones/:id', name: 'DetalleLiquidacion', component: DetalleLiquidacionView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial'] } },

        // Gestión
        { path: 'terceros', name: 'Terceros', component: TercerosView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial'] } },

        // Rumas
        { path: 'rumas', name: 'Rumas', component: RumasView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial'] } },
        { path: 'rumas/:id', name: 'DetalleRuma', component: DetalleRumaView, meta: { roles: ['Admin', 'Gerencia', 'Comercial', 'JefeComercial'] } },
        { path: 'administracion/campanas', name: 'Campanas', component: CampanasView, meta: { roles: ['Admin', 'Gerencia'] } },

        // Administración (vista unificada con tabs: Usuarios / Parámetros / Notificaciones)
        { path: 'administracion', name: 'Administracion', component: () => import('@/views/admin/AdminView.vue'), meta: { roles: ['Admin'] } },
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

  // Guard por roles específicos de ruta (meta.roles)
  if (to.meta.roles) {
    const rol = auth.user?.rol ?? ''
    if (!(to.meta.roles as string[]).includes(rol)) return { name: 'Unauthorized' }
  }



  return true
})

export default router
