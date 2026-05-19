<template>

  </template>

  <script setup lang="ts">

  </script>

  <style scoped>
  .ag-badge {
    background: #6366f1; color: #fff;
    border-radius: 4px; padding: 1px 8px;
    font-size: 0.8rem; font-weight: 700;
  }
  .req { color: var(--color-danger); margin-left: 2px; }

  .preview-box {
    background: var(--color-bg-2, rgba(255,255,255,0.03));
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-top: 0.25rem;
  }
  .preview-titulo {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    color: var(--color-text-faint);
    margin-bottom: 0.75rem;
    text-transform: uppercase;
  }
  .preview-grid {
    display: flex; gap: 2rem; flex-wrap: wrap;
  }
  .preview-item {
    display: flex; flex-direction: column; gap: 0.2rem;
  }
  .preview-label {
    font-size: 0.68rem;
    color: var(--color-text-faint);
    font-family: var(--font-mono);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .preview-val {
    font-family: var(--font-mono);
    font-size: var(--text-lg);
    color: var(--color-text);
  }
  .preview-val.gold { color: var(--color-gold); font-weight: 600; }
  .preview-warn {
    margin-top: 0.75rem;
    font-size: 0.78rem;
    color: #d97706;
  }
  </style>
