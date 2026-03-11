import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { public: true },
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
          component: () => import('@/views/balanza/BalanzaView.vue'),
        },
        {
          path: 'balanza/nuevo',
          name: 'RegistrarCamion',
          component: () => import('@/views/balanza/RegistrarCamionView.vue'),
        },
        {
          path: 'balanza/:id',
          name: 'SesionBalanza',
          component: () => import('@/views/balanza/SesionView.vue'),
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
    return { name: 'login' }
  }

  if (!store.user) {
    try {
      await store.fetchMe()
    } catch {
      store.clearTokens()
      return { name: 'login' }
    }
  }

  return true
})

export default router
