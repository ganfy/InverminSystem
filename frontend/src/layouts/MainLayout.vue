<template>
  <div class="app-layout">

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
            <span class="nav-icon">{{ item.icon }}</span>
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
import { ref, computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { NAV_CONFIG } from '@/router/nav'
import type { NavSection } from '@/router/nav'

const authStore = useAuthStore()
const router    = useRouter()
const route     = useRoute()

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
  font-size: 1.1rem;
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
  font-size: 0.8rem;
  color: var(--color-gold-light);
  letter-spacing: 0.1em;
}

.sidebar-subtitle {
  font-size: 0.65rem;
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
  font-size: 0.6rem;
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
  font-size: 0.85rem;
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
  font-size: 0.9rem;
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
  font-size: 0.8rem;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-user-rol {
  font-size: 0.65rem;
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
  font-size: 1rem;
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
    margin-left: 220px;
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
  font-size: 1.3rem;
  cursor: pointer;
  line-height: 1;
  padding: 0;
}

.topbar-title {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--color-text-muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* ── Contenido ───────────────────────────────────────────────── */
.main-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}
</style>
