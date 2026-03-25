<template>
  <div class="login-bg">

    <!-- Logo -->
    <div class="logo-area">
      <div class="logo-placeholder">
        <!-- Reemplazar con: <img src="@/assets/logo.png" alt="Logo" class="logo-img" /> -->
        <span class="logo-symbol">✹</span>
      </div>
      <p class="app-title">INVERMIN PAITITI</p>
    </div>

    <!-- Formulario -->
    <form class="login-form" @submit.prevent="handleLogin">
      <input
        v-model="username"
        type="text"
        class="field-input"
        placeholder="Usuario"
        autocomplete="username"
        :disabled="loading"
      />
      <input
        v-model="password"
        type="password"
        class="field-input"
        placeholder="Contraseña"
        autocomplete="current-password"
        :disabled="loading"
      />

      <p v-if="error" class="error-msg">{{ error }}</p>

      <button
        type="submit"
        :class="['btn-primary', 'btn-login', { ready: username && password }]"
        :disabled="loading"
      >
        <span v-if="loading" class="spinner" />
        <span v-else>Ingresar</span>
      </button>
    </form>

    <p class="version">v2.0 · Planta Paititi</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router    = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading  = ref(false)
const error    = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = 'Ingrese usuario y contraseña'
    return
  }
  loading.value = true
  error.value   = ''
  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Error al iniciar sesión'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-bg {
  min-height: 100vh;
  background-color: var(--color-bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  padding: 2rem 1rem;
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.logo-placeholder {
  width: 96px;
  height: 96px;
  border: 2px solid var(--color-gold);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-gold-bg);
}

.logo-symbol {
  font-size: var(--text-xxxl);
  color: var(--color-gold);
  line-height: 1;
}

.logo-img {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  object-fit: cover;
}

.app-title {
  font-family: var(--font-mono);
  font-size: var(--text-base);
  color: var(--color-gold-light);
  letter-spacing: 0.15em;
  text-align: center;
}

.login-form {
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-form .field-input {
  padding: 1rem 1.25rem;
  font-size: var(--text-base);
  border-radius: var(--radius-md);
}

.btn-login {
  width: 100%;
  margin-top: 0.5rem;
  padding: 1rem;
  font-size: var(--text-base);
  border-radius: var(--radius-md);
}

@media (min-width: 768px) {
  .login-form {
    max-width: 520px;
  }
}

.version {
  font-size: var(--text-sm);
  color: var(--color-text-faint);
  letter-spacing: 0.1em;
}
</style>
