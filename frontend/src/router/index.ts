import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginView from '@/views/auth/LoginView.vue'
import BalanzaView from '@/views/balanza/BalanzaView.vue'
import RegistrarCamionView from '@/views/balanza/RegistrarCamionView.vue'
import SesionView from '@/views/balanza/SesionView.vue'
import MuestreoView from '@/views/muestreo/MuestreoView.vue'
import PruebasView from '@/views/pruebas/PruebasView.vue'
import RegistrarPruebasView from '@/views/pruebas/RegistrarPruebasView.vue'
import LaboratorioView from '@/views/laboratorio/LaboratorioDashboardView.vue'
import RegistrarLeyView from '@/views/laboratorio/RegistrarLeyView.vue'
import RegistrarRecuperacionView from '@/views/laboratorio/RegistrarRecuperacionView.vue'
import DetalleLoteView from '@/views/laboratorio/DetalleLoteView.vue'
import UnauthorizedView from '@/views/auth/UnauthorizedView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'
import MainLayout from '@/layouts/MainLayout.vue'
import RegistrarHumedadView from '@/views/muestreo/RegistrarHumedadView.vue'
import ImportarCertificadoLeyView from '@/views/laboratorio/ImportarCertificadoLeyView.vue'
import ImportarCertificadoRecuperacionView from '@/views/laboratorio/ImportarCertificadoRecView.vue'

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
        { path: 'dashboard', name: 'Dashboard', component: DashboardView },

        // Balanza
        { path: 'balanza', name: 'Balanza', component: BalanzaView },
        { path: 'balanza/nueva', name: 'NuevaSesion', component: RegistrarCamionView },
        { path: 'balanza/:id', name: 'SesionDetalle', component: SesionView },

        // Muestreo
        { path: 'muestreo', name: 'Muestreo', component: MuestreoView },
        { path: 'muestreo/:ip', name: 'RegistrarHumedad', component: RegistrarHumedadView },

        // Pruebas
        { path: 'pruebas', name: 'Pruebas', component: PruebasView },
        { path: 'pruebas/:ip', name: 'RegistrarPrueba', component: RegistrarPruebasView },

        // Laboratorio
        { path: 'laboratorio', name: 'Laboratorio', component: LaboratorioView },
        { path: 'laboratorio/ley/:cip', name: 'RegistrarLey', component: RegistrarLeyView },
        { path: 'laboratorio/recuperacion/:cip', name: 'RegistrarRecuperacion', component: RegistrarRecuperacionView },
        { path: 'laboratorio/lote/:ip', name: 'DetalleLote', component: DetalleLoteView },
        { path: 'laboratorio/importar-ley/:cip', name: 'ImportarCertLey', component: ImportarCertificadoLeyView },
        { path: 'laboratorio/importar-rec/:cip', name: 'ImportarCertRec', component: ImportarCertificadoRecuperacionView },
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
              case 'Comercial':
                return '/dashboard'
              case 'Balanza':
                return '/balanza'
              case 'Muestreo':
                return '/muestreo'
              case 'Laboratorista':
                return '/laboratorio'
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

  // Protección específica de DetalleLote
  if (to.name === 'DetalleLote') {
    const rol = auth.user?.rol ?? ''
    const permitidos = ['Admin', 'Gerencia', 'Comercial']
    if (!permitidos.includes(rol)) return { name: 'Unauthorized' }
  }

  return true
})

export default router
