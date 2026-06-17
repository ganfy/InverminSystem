<template>
  <RouterView />
  <AppToasts />
  <AppConfirm />
  <AppPrompt />
  <!-- Widget de accesibilidad: visible en toda la app cuando hay sesión activa -->
  <AccessibilityWidget v-if="authStore.isAuthenticated" />
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { RouterView } from 'vue-router'
import AppToasts          from '@/components/AppToasts.vue'
import AppConfirm         from '@/components/AppConfirm.vue'
import AppPrompt          from '@/components/AppPrompt.vue'
import AccessibilityWidget from '@/components/AccessibilityWidget.vue'
import { useAuthStore }   from '@/stores/auth'
import { useAccessibilityStore } from '@/stores/accessibility'

const authStore = useAuthStore()
const a11yStore = useAccessibilityStore()

// Inicializar preferencias cuando el usuario está autenticado
// (carga desde localStorage por userId y aplica las variables CSS)
watch(
  () => authStore.user,
  (user) => {
    if (user) {
      // Usamos el username como identificador único (siempre disponible en UsuarioMe)
      a11yStore.init(user.id)
    } else {
      a11yStore.reset()
    }
  },
  { immediate: true },
)
</script>
