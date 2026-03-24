<template>
    <div class="unauthorized-page">
      <div class="card error-card">
        <div class="error-icon">🚫</div>
        <h2>Acceso Denegado</h2>
        <p>No tienes los permisos necesarios para ver esta página.</p>
        <div class="btn-container">
          <button class="btn-primary ready" @click="irAlInicio">
            Volver al Inicio
          </button>
        </div>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { useRouter } from 'vue-router'

  const router = useRouter()

  function irAlInicio() {
    router.push('/')
  }
  </script>

  <style scoped>
  .unauthorized-page {
    display: flex; justify-content: center; align-items: center; height: 100vh;
    background-color: var(--color-bg);
  }
  .error-card {
    text-align: center; padding: 3rem 4rem;
    border: 1px solid var(--color-error); border-radius: var(--radius-md);
    max-width: 450px; background: var(--color-bg-card);
  }
  .error-icon { font-size: 3rem; margin-bottom: 1rem; }
  h2 { color: var(--color-error); margin-bottom: 0.5rem; font-family: var(--font-mono); }
  p { color: var(--color-text-muted); margin-bottom: 2rem; line-height: 1.5; }

  .btn-container {
    display: flex;
    justify-content: center;
  }
  </style>
