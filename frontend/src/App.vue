<template>
  <RouterView />
  <AppToasts />
  <AppConfirm />
  <AppPrompt />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppToasts  from '@/components/AppToasts.vue'
import AppConfirm from '@/components/AppConfirm.vue'
import AppPrompt  from '@/components/AppPrompt.vue'
</script>
