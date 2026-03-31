import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import LoginView from '@/views/auth/LoginView.vue'
import BalanzaView from '@/views/balanza/BalanzaView.vue'
import RegistrarCamionView from '@/views/balanza/RegistrarCamionView.vue'
import SesionView from '@/views/balanza/SesionView.vue'
import MuestreoView from '@/views/muestreo/MuestreoView.vue'
import RegistrarHumedadView from '@/views/muestreo/RegistrarHumedadView.vue'
import PruebasView from '@/views/pruebas/PruebasView.vue'
import RegistrarPruebasView from '@/views/pruebas/RegistrarPruebasView.vue'

import UnauthorizedView from '@/views/auth/UnauthorizedView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => LoginView,
      meta: { public: true },
    },
    {
      path: '/unauthorized',
      name: 'Unauthorized',
      component: UnauthorizedView,
      meta: { requiresAuth: true }, // Requiere estar logueado para ver este error
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
        },
        {
          path: 'terceros',
          name: 'Terceros',
          component: () => import('@/views/terceros/TercerosView.vue'),
        },
        {
          path: 'balanza',
          name: 'Balanza',
          component: BalanzaView,
        },
        {
          path: 'balanza/nuevo',
          name: 'RegistrarCamion',
          component: RegistrarCamionView,
        },
        {
          path: 'balanza/:id',
          name: 'SesionBalanza',
          component: SesionView,
        },
        {
          path: 'muestreo',
          name: 'Muestreo',
          component: MuestreoView,
        },
        {
          path: 'muestreo/:ip/registrar',
          name: 'RegistrarHumedad',
          component: () => import('@/views/muestreo/RegistrarHumedadView.vue'),
        },
        {
          path: 'pruebas',
          name: 'PruebasMetalurgicas',
          component: PruebasView,
        },
        {
          path: 'pruebas/:ip/registrar',
          name: 'RegistrarPrueba',
          component: RegistrarPruebasView,

        }
      ],
    },
    {
      path: '/admin/usuarios',
      component: () => import('@/views/admin/UsuariosView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach(async (to) => {
  const store = useAuthStore()

  if (to.meta.public) {
    return true
  }

  if (!store.isAuthenticated) {
    return { name: 'Login' }
  }

  if (!store.user) {
    try {
      await store.fetchMe()
    } catch {
      store.clearTokens()
      return { name: 'Login' }
    }
  }
  // -----------------------------------------------------------
  // CONTROL DE ACCESO BASADO EN ROLES Y RUTAS (Path Intercept)
  // -----------------------------------------------------------

  // 1. Proteger rutas de Administración (Solo para rol 'Admin')
  if (to.path.startsWith('/admin')) {
    if (store.rol !== 'Admin') {
      return { name: 'Unauthorized' }
    }
  }

  // 2. Proteger rutas de Balanza (Solo Admin o Balancero)
  // if (to.path.startsWith('/balanza')) {
  //   if (store.rol !== 'Admin' && store.rol !== 'Balancero') {
  //     return { name: 'Unauthorized' }
  //   }
  // }

  return true
})

export default router
