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

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ── Auth ────────────────────────────────────────────────────────────────
    { path: '/login', name: 'Login', component: LoginView },
    { path: '/unauthorized', name: 'Unauthorized', component: UnauthorizedView, meta: { requiresAuth: true } },

    // ── Balanza ─────────────────────────────────────────────────────────────
    { path: '/balanza', name: 'Balanza', component: BalanzaView, meta: { requiresAuth: true } },
    { path: '/balanza/nueva', name: 'NuevaSesion', component: RegistrarCamionView, meta: { requiresAuth: true } },
    { path: '/balanza/:id', name: 'SesionDetalle', component: SesionView, meta: { requiresAuth: true } },

    // ── Muestreo ────────────────────────────────────────────────────────────
    { path: '/muestreo', name: 'Muestreo', component: MuestreoView, meta: { requiresAuth: true } },

    // ── Pruebas Metalúrgicas ─────────────────────────────────────────────────
    { path: '/pruebas', name: 'Pruebas', component: PruebasView, meta: { requiresAuth: true } },
    { path: '/pruebas/:ip', name: 'RegistrarPrueba', component: RegistrarPruebasView, meta: { requiresAuth: true } },

    // ── Laboratorio ──────────────────────────────────────────────────────────
    {
      path: '/laboratorio',
      name: 'Laboratorio',
      component: LaboratorioView,
      meta: { requiresAuth: true },
    },
    {
      // Laboratorista registra ley desde su CIP
      path: '/laboratorio/ley/:cip',
      name: 'RegistrarLey',
      component: RegistrarLeyView,
      meta: { requiresAuth: true },
    },
    {
      // Laboratorista registra recuperación desde su CIP
      path: '/laboratorio/recuperacion/:cip',
      name: 'RegistrarRecuperacion',
      component: RegistrarRecuperacionView,
      meta: { requiresAuth: true },
    },
    {
      // Comercial/Gerencia/Admin ven detalle por IP de lote
      path: '/laboratorio/lote/:ip',
      name: 'DetalleLote',
      component: DetalleLoteView,
      meta: { requiresAuth: true },
    },

    // ── Redirect raíz ────────────────────────────────────────────────────────
    { path: '/', redirect: '/login' },
  ],
})

// ── Guard de autenticación ────────────────────────────────────────────────────
router.beforeEach((to) => {
  if (!to.meta.requiresAuth) return true

  const auth = useAuthStore()
  if (!auth.accessToken) return { name: 'Login' }

  // Proteger detalle de lote solo para roles que pueden ver IPs
  if (to.name === 'DetalleLote') {
    const rol = auth.user?.rol ?? ''
    const permitidos = ['Admin', 'Gerencia', 'Comercial']
    if (!permitidos.includes(rol)) return { name: 'Unauthorized' }
  }

  return true
})

export default router
