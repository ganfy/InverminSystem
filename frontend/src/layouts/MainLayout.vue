<template>
  <div class="app-layout" :class="{ 'app-layout--offline': !online }">

    <!-- Overlay mobile -->
    <div
      v-if="sidebarOpen"
      class="sidebar-overlay"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside :class="['sidebar', { 'sidebar--open': sidebarOpen }]">

      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="sidebar-logo-img">
          <!-- <img src="@/assets/logo.png" alt="Logo" /> -->
          <span>✹</span>
        </div>
        <div class="sidebar-logo-text">
          <p class="sidebar-title">INVERMIN</p>
          <p class="sidebar-subtitle">PAITITI</p>
        </div>
      </div>

      <!-- Nav -->
      <nav class="sidebar-nav">
        <template v-for="section in visibleSections" :key="section.section">
          <p class="nav-section-label">{{ section.section }}</p>
          <RouterLink
            v-for="item in visibleItems(section)"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            active-class="nav-item--active"
            exact-active-class="nav-item--active"
            @click="sidebarOpen = false"
          >
          <component :is="item.icon" :size="20" class="nav-icon" />
          <span>{{ item.label }}</span>
          </RouterLink>
        </template>
      </nav>

      <!-- Usuario + logout -->
      <div class="sidebar-footer">
        <div class="sidebar-user">
          <p class="sidebar-user-name">{{ authStore.user?.nombre_completo }}</p>
          <p class="sidebar-user-rol">{{ authStore.user?.rol }}</p>
        </div>
        <button class="btn-logout" @click="handleLogout" title="Cerrar sesión">
          ⏻
        </button>
      </div>
    </aside>

    <!-- Contenido principal -->
    <div class="main-wrapper">

      <SyncIndicator
        :online="online"
        :sincronizando="sincronizando"
        :pendientes="pendientes"
        :ips-restantes="ipsRestantes"
        :ultimo-sync="ultimoSync"
        :error-sync="errorSync"
        :mostrar-ips="isBalanzaRoute"
        @sync="sincronizar"
        style="margin-left: auto; margin-right: 1rem;"
      />

      <!-- Topbar mobile -->
      <header class="topbar">
        <button class="hamburger" @click="sidebarOpen = !sidebarOpen">
          <span :class="['hamburger-icon', { 'hamburger-icon--open': sidebarOpen }]">☰</span>
        </button>
        <p class="topbar-title">{{ currentTitle }}</p>
      </header>

      <main class="main-content">
        <RouterView />
      </main>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSync } from '@/composables/useSync'
import SyncIndicator from '@/components/balanza/SyncIndicator.vue'
import { NAV_CONFIG } from '@/router/nav'
import type { NavSection } from '@/router/nav'

const authStore = useAuthStore()
const router    = useRouter()
const route     = useRoute()
const isBalanzaRoute = computed(() => route.path.startsWith('/balanza'))

const {
  online,
  sincronizando,
  pendientes,
  ipsRestantes,
  ultimoSync,
  errorSync,
  inicializar,
  sincronizar
} = useSync()

// Al autenticarse, inicializar el sistema offline
watch(
  () => authStore.isAuthenticated,
  async (autenticado) => {
    if (autenticado) await inicializar()
  },
  { immediate: true },
)

const sidebarOpen = ref(false)
const rol = computed(() => authStore.user?.rol ?? '')

function tieneAcceso(roles?: string[]) {
  if (!roles || roles.length === 0) return true
  return roles.includes(rol.value)
}

const visibleSections = computed(() =>
  NAV_CONFIG.filter(s => tieneAcceso(s.roles))
)

function visibleItems(section: NavSection) {
  return section.items.filter(i => tieneAcceso(i.roles))
}

const currentTitle = computed(() => {
  for (const section of NAV_CONFIG) {
    const item = section.items.find(i => i.path === route.path)
    if (item) return item.label
  }
  return ''
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

watch(() => online.value, (isOnline) => {
  if (!isOnline) {
    // Si se va el internet, le aplicamos la clase al <body> del navegador (no solo a la app)
    document.body.classList.add('modo-offline')
  } else {
    // Si regresa, se la quitamos
    document.body.classList.remove('modo-offline')
  }
}, { immediate: true })
</script>

<style scoped>
/* ── Layout base ─────────────────────────────────────────────── */
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

/* ── Sidebar ─────────────────────────────────────────────────── */
.sidebar {
  width: 220px;
  min-height: 100vh;
  background: #1e1e16;
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 100;
  transform: translateX(-100%);
  transition: transform 0.25s ease;
}

/* Desktop: siempre visible */
@media (min-width: 768px) {
  .sidebar {
    transform: translateX(0);
    position: sticky;
    top: 0;
    height: 100vh;
  }
}

/* Mobile: abierto */
.sidebar--open {
  transform: translateX(0);
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 99;
}

/* ── Logo ───────────────────────────────────────────────────── */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1rem;
  border-bottom: 1px solid var(--color-border);
}

.sidebar-logo-img {
  width: 40px;
  height: 40px;
  border: 1px solid var(--color-gold);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-gold);
  font-size: var(--text-base);
  flex-shrink: 0;
}

.sidebar-logo-img img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.sidebar-title {
  font-family: var(--font-mono);
  font-size: var(--text-md);
  color: var(--color-gold-light);
  letter-spacing: 0.1em;
}

.sidebar-subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-dim);
  letter-spacing: 0.15em;
}

/* ── Nav ────────────────────────────────────────────────────── */
.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.nav-section-label {
  font-size: var(--text-xs);
  letter-spacing: 0.2em;
  color: var(--color-text-faint);
  padding: 0.75rem 1rem 0.25rem;
  font-weight: 700;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 1rem;
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: var(--text-md);
  font-family: var(--font-main);
  letter-spacing: 0.05em;
  transition: color 0.15s, background 0.15s;
  border-left: 2px solid transparent;
}

.nav-item:hover {
  color: var(--color-text);
  background: rgba(184, 150, 46, 0.05);
}

.nav-item--active {
  color: var(--color-gold-light);
  border-left-color: var(--color-gold);
  background: rgba(184, 150, 46, 0.08);
}

.nav-icon {
  font-size: var(--text-base);
  width: 18px;
  text-align: center;
  flex-shrink: 0;
}

/* ── Footer ─────────────────────────────────────────────────── */
.sidebar-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  gap: 0.5rem;
}

.sidebar-user {
  overflow: hidden;
}

.sidebar-user-name {
  font-size: var(--text-md);
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-user-rol {
  font-size: var(--text-xs);
  color: var(--color-text-dim);
  letter-spacing: 0.08em;
}

.btn-logout {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  border-radius: var(--radius-sm);
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-size: var(--text-base);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: color 0.15s, border-color 0.15s;
}

.btn-logout:hover {
  color: var(--color-error);
  border-color: var(--color-error);
}

/* ── Main wrapper ────────────────────────────────────────────── */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

@media (min-width: 768px) {
  .main-wrapper {
    margin-left: 5%;
    margin-right: 5%;
    margin-top: 1%;
  }
}

/* ── Topbar mobile ───────────────────────────────────────────── */
.topbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: #1e1e16;
  position: sticky;
  top: 0;
  z-index: 50;
}

@media (min-width: 768px) {
  .topbar {
    display: none;
  }
}

.hamburger {
  background: transparent;
  border: none;
  color: var(--color-gold);
  font-size: var(--text-base);
  cursor: pointer;
  line-height: 1;
  padding: 0;
}

.topbar-title {
  font-family: var(--font-mono);
  font-size: var(--text-md);
  color: var(--color-text-muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* ── Contenido ───────────────────────────────────────────────── */
.main-content {
  flex: 1;
  padding: var(--page-padding);
  overflow-y: auto;
}

/* ── Estado Offline (Advertencia Visual) ─────────────────────── */

/* 1. Cinta superior de precaución */
.app-layout--offline::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 7px; /* Grosor de la línea superior */
  /* Patrón de franjas rojas y transparentes/oscuras */
  background: repeating-linear-gradient(
    45deg,
    var(--color-error, #d32f2f),
    var(--color-error, #d32f2f) 15px,
    #b71c1c 15px,
    #b71c1c 30px
  );
  z-index: 9999; /* Asegura que esté por encima de todo */
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(161, 33, 33, 0.4);
  animation: slide-bg 2s linear infinite; /* Pequeña animación opcional */
}

/* Animación sutil para la cinta de precaución */
@keyframes slide-bg {
  0% { background-position: 0 0; }
  100% { background-position: 42px 0; }
}
</style>
