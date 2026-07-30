<template>
  <div class="page-container">
    <header class="page-header">
      <div class="header-title-row">
        <Settings class="header-icon animate-spin-slow" :size="28" />
        <div>
          <h1 class="page-title">Configuración del Sistema</h1>
          <p class="page-subtitle">Parámetros de cálculo metalúrgico y notificaciones globales</p>
        </div>
      </div>
    </header>

    <!-- ── Sección: Constantes de Cálculo ─────────────────────────────────── -->
    <section class="config-section">
      <div class="section-header-row">
        <Database class="section-icon" :size="20" />
        <h2 class="section-title">Constantes de Cálculo Metalúrgico</h2>
      </div>

      <div v-if="cargandoCalculo" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem" /> Cargando constantes…
      </div>

      <div v-else class="settings-grid">
        <div 
          v-for="c in constantes" 
          :key="c.clave" 
          class="setting-card" 
          :class="{ 'card-modified': editsCalculo[c.clave] !== c.valor }"
        >
          <div class="setting-info">
            <div class="setting-header">
              <span class="setting-title">{{ NOMBRES_AMIGABLES[c.clave] || c.clave }}</span>
              <div class="badges-group">
                <code class="code-badge">{{ c.clave }}</code>
                <span v-if="!c.en_bd" class="badge-default">Valor Default</span>
                <span v-else class="badge-custom">
                  <Database :size="10" style="margin-right: 3px;" />
                  Base de Datos
                </span>
              </div>
            </div>
            <p class="setting-description">{{ c.descripcion }}</p>
            <div class="setting-meta">
              <Info :size="12" class="meta-icon" />
              <span class="meta-label">Valor por defecto:</span>
              <span class="meta-value">{{ c.default }} <span class="meta-unit">{{ UNIDADES[c.clave] }}</span></span>
            </div>
          </div>

          <div class="setting-action-group">
            <div class="field">
              <label class="field-label">Valor Actual</label>
              <div class="input-with-button">
                <div class="input-wrapper">
                  <select
                    v-if="c.clave.startsWith('redondeo_ley_')"
                    v-model="editsCalculo[c.clave]"
                    class="field-input field-select select-valor"
                    :class="{ modified: editsCalculo[c.clave] !== c.valor }"
                  >
                    <option value="normal">Normal / Matemático (.5 sube)</option>
                    <option value="abajo">Hacia Abajo (Truncar)</option>
                    <option value="arriba">Hacia Arriba</option>
                    <option value="bancario">Bancario / Par (.5 par)</option>
                  </select>
                  <input
                    v-else
                    v-model="editsCalculo[c.clave]"
                    type="text"
                    class="field-input input-valor"
                    :class="{ modified: editsCalculo[c.clave] !== c.valor }"
                  />
                  <span v-if="UNIDADES[c.clave]" class="input-unit">{{ UNIDADES[c.clave] }}</span>
                </div>
                <button
                  class="btn-save-inline"
                  :disabled="guardandoCalculo[c.clave] || editsCalculo[c.clave] === c.valor"
                  @click="guardarConstante(c.clave)"
                  title="Guardar cambio"
                >
                  <span v-if="guardandoCalculo[c.clave]" class="spinner spinner-sm" />
                  <span v-else class="btn-content">
                    <Save :size="14" />
                    <span>Guardar</span>
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="nota-info-card">
        <AlertTriangle :size="16" class="warn-icon" />
        <p class="nota-text">
          <strong>Aviso de recálculo:</strong> Los cambios aplicarán a partir de la siguiente operación registrada. Los lotes ya liquidados no se verán afectados. Modificaciones restringidas a administradores.
        </p>
      </div>
    </section>

    <!-- ── Sección: Notificaciones Telegram ───────────────────────────────── -->
    <section class="config-section">
      <div class="section-header-row">
        <Bot class="section-icon" :size="20" />
        <h2 class="section-title">Notificaciones por Telegram</h2>
      </div>

      <div v-if="cargandoTelegram" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem" /> Cargando configuración de Telegram…
      </div>

      <div v-else class="config-card-premium">
        <div class="card-status-header">
          <div class="status-indicator-group">
            <span :class="['tg-indicator-glow', telegramCfg.configurado ? 'activo' : 'inactivo']" />
            <span class="status-text">{{ telegramCfg.configurado ? 'Servicio de Notificaciones Activo' : 'Servicio Desconfigurado' }}</span>
          </div>
          <span class="status-badge" :class="telegramCfg.configurado ? 'configured' : 'unconfigured'">
            {{ telegramCfg.configurado ? 'Conectado' : 'Sin conexión' }}
          </span>
        </div>

        <div class="tg-fields-grid">
          <!-- Token del Bot -->
          <div v-if="!telegramCfg.desde_env" class="field field-full">
            <label class="field-label">Token del Bot (Telegram API)</label>
            <div class="input-with-icon">
              <input
                v-model="editsTelegram.bot_token"
                type="password"
                class="field-input input-con-icono"
                placeholder="1234567890:ABCdef..."
                autocomplete="off"
              />
              <Bot :size="16" class="input-icon" />
            </div>
            <p class="field-hint">
              Obtén un token creando un bot con el bot oficial <a href="https://t.me/BotFather" target="_blank" class="link-gold">@BotFather</a>.
            </p>
          </div>
          <div v-else class="field field-full">
            <div class="info-alert-box">
              <Info :size="16" class="info-icon" />
              <p class="info-text">
                El token del bot está configurado en las variables de entorno del servidor. Si necesitas cambiarlo, contacta al administrador del sistema.
              </p>
            </div>
          </div>

          <!-- Chat ID -->
          <div class="field">
            <label class="field-label">Chat ID de Destino</label>
            <div class="input-with-icon">
              <input
                v-model="editsTelegram.chat_id"
                type="text"
                class="field-input input-con-icono"
                placeholder="-100123456789 o tu ID"
              />
              <MessageSquare :size="16" class="input-icon" />
            </div>
            <p class="field-hint">
              Usa <a href="https://t.me/userinfobot" target="_blank" class="link-gold">@userinfobot</a> para obtener tu ID personal, o el ID de tu canal/grupo.
            </p>
          </div>

          <!-- Hora del resumen -->
          <div class="field">
            <label class="field-label">Hora del Resumen Diario</label>
            <div class="input-with-icon">
              <input
                v-model="editsTelegram.hora_resumen"
                type="time"
                class="field-input input-con-icono"
              />
              <Clock :size="16" class="input-icon" />
            </div>
            <p class="field-hint">
              Se enviará un resumen con todas las alertas activas a esta hora cada día.
            </p>
          </div>
        </div>

        <div class="tg-actions">
          <button
            class="btn-save-inline btn-primary-premium"
            :disabled="guardandoTelegram"
            @click="guardarTelegram"
          >
            <span v-if="guardandoTelegram" class="spinner spinner-sm" />
            <span v-else class="btn-content">
              <Save :size="14" />
              <span>Guardar Configuración</span>
            </span>
          </button>
          <button
            class="btn-secondary-premium"
            :disabled="!telegramCfg.configurado || probandoTelegram"
            @click="probarTelegram"
          >
            <span v-if="probandoTelegram" class="spinner spinner-sm" />
            <span v-else class="btn-content">
              <Send :size="14" />
              <span>Enviar Mensaje de Prueba</span>
            </span>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { adminApi, type ConstanteCalculo } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import { Settings, Save, Send, Bot, Database, AlertTriangle, Info, Clock, MessageSquare } from 'lucide-vue-next'

const ui = useUiStore()

// Mapeos para visualización premium
const NOMBRES_AMIGABLES: Record<string, string> = {
  factor_oz_tc: 'Factor de Conversión (Oz/TC → Gr/TM)',
  umbral_volado_oz_tc: 'Umbral de Ley para Lote Volado',
  blank_correction_ag: 'Corrección en Blanco de Plata (Ag)',
  proximo_ip: 'IP Inicial del Próximo Bloque (Balanza Offline)',
  tamano_bloque_ip: 'Tamaño del Bloque de IPs (Balanza Offline)',
  proximo_ticket: 'Ticket Inicial del Próximo Bloque (Balanza Offline)',
  tamano_bloque_ticket: 'Tamaño del Bloque de Tickets (Balanza Offline)',
  costo_fijo_planta_maquila: 'Costo Fijo Planta para Maquila',
  decimales_ley_laboratorio: 'Decimales Ley Laboratorio',
  decimales_ley_planta: 'Decimales Ley Planta',
  decimales_ley_comercial: 'Decimales Ley Comercial',
  decimales_ley_final: 'Decimales Ley Final',
  redondeo_ley_laboratorio: 'Redondeo Ley Laboratorio',
  redondeo_ley_planta: 'Redondeo Ley Planta',
  redondeo_ley_comercial: 'Redondeo Ley Comercial',
  redondeo_ley_final: 'Redondeo Ley Final',
}

const UNIDADES: Record<string, string> = {
  factor_oz_tc: 'Gr/TM',
  umbral_volado_oz_tc: 'Oz/TC',
  blank_correction_ag: 'mg',
  proximo_ip: '#',
  proximo_ticket: '#',
  tamano_bloque_ip: 'IPs',
  tamano_bloque_ticket: 'tickets',
  costo_fijo_planta_maquila: 'USD/TM',
}

// Claves críticas que requieren advertencia especial al editar
const CLAVES_CRITICAS = new Set(['proximo_ip', 'proximo_ticket'])

// ── Constantes de cálculo ───────────────────────────────────────────────────
const cargandoCalculo  = ref(true)
const constantes       = ref<ConstanteCalculo[]>([])
const editsCalculo     = reactive<Record<string, string>>({})
const guardandoCalculo = reactive<Record<string, boolean>>({})

async function cargarConstantes() {
  cargandoCalculo.value = true
  try {
    constantes.value = await adminApi.getConstantesCalculo()
    for (const c of constantes.value) editsCalculo[c.clave] = c.valor
  } catch {
    ui.toast('Error al cargar constantes', 'error')
  } finally {
    cargandoCalculo.value = false
  }
}

async function guardarConstante(clave: string) {
  const valor = editsCalculo[clave]?.trim()
  if (!valor) return

  const esCritica = CLAVES_CRITICAS.has(clave)
  const mensaje = esCritica
    ? `Atención: Estás cambiando "${clave}" a ${valor}.\n\nEsto define desde qué número comenzará el próximo bloque de IPs/Tickets reservado para la balanza offline.\n\n• Si el valor ya fue asignado antes, se generarán colisiones al sincronizar.\n• El cambio aplica en el próximo login o sincronización del operador de balanza.\n\n¿Confirmar cambio?`
    : `¿Cambiar "${clave}" a ${valor}? Afecta futuros cálculos de ley.`

  const ok = await ui.showConfirm({
    title: esCritica ? 'Cambio crítico de numeración' : 'Actualizar constante',
    message: mensaje,
    confirmLabel: 'Confirmar',
    danger: esCritica
  })
  if (!ok) return

  guardandoCalculo[clave] = true
  try {
    await adminApi.updateConstante(clave, valor)
    ui.toast(`"${clave}" actualizado`, 'success')
    await cargarConstantes()
  } catch {
    ui.toast('Error al guardar', 'error')
  } finally {
    guardandoCalculo[clave] = false
  }
}

// ── Telegram ────────────────────────────────────────────────────────────────
const cargandoTelegram  = ref(true)
const guardandoTelegram = ref(false)
const probandoTelegram  = ref(false)

interface TelegramCfg { bot_token: string; chat_id: string; hora_resumen: string; configurado: boolean; desde_env?: boolean }
const telegramCfg   = ref<TelegramCfg>({ bot_token: '', chat_id: '', hora_resumen: '07:00', configurado: false, desde_env: false })
const editsTelegram = reactive({ bot_token: '', chat_id: '', hora_resumen: '07:00' })

async function cargarTelegram() {
  cargandoTelegram.value = true
  try {
    const cfg = await adminApi.getTelegramConfig()
    telegramCfg.value = cfg
    // No pre-llenamos el token (viene enmascarado)
    editsTelegram.chat_id      = cfg.chat_id
    editsTelegram.hora_resumen = cfg.hora_resumen || '07:00'
    editsTelegram.bot_token    = ''
  } catch {
    ui.toast('Error al cargar config Telegram', 'error')
  } finally {
    cargandoTelegram.value = false
  }
}

async function guardarTelegram() {
  if (!telegramCfg.value.desde_env && !editsTelegram.bot_token && !telegramCfg.value.configurado) {
    ui.toast('Ingresa el token del bot', 'warning')
    return
  }
  guardandoTelegram.value = true
  try {
    const payload = {
      bot_token:    editsTelegram.bot_token || '(mantener)',
      chat_id:      editsTelegram.chat_id,
      hora_resumen: editsTelegram.hora_resumen,
    }
    await adminApi.updateTelegramConfig(payload)
    ui.toast('Configuración de Telegram guardada', 'success')
    await cargarTelegram()
  } catch {
    ui.toast('Error al guardar configuración', 'error')
  } finally {
    guardandoTelegram.value = false
  }
}

async function probarTelegram() {
  probandoTelegram.value = true
  try {
    await adminApi.testTelegram()
    ui.toast('¡Mensaje de prueba enviado! Revisa tu Telegram.', 'success')
  } catch {
    ui.toast('No se pudo enviar. Verifica el token y chat ID.', 'error')
  } finally {
    probandoTelegram.value = false
  }
}

onMounted(async () => {
  await Promise.all([cargarConstantes(), cargarTelegram()])
})
</script>

<style scoped>
.config-section {
  margin-bottom: 3rem;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  color: var(--color-gold);
}

.animate-spin-slow {
  animation: spin 8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.section-header-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.section-icon {
  color: var(--color-gold);
  opacity: 0.85;
}

.section-title {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  color: var(--color-text-primary);
  margin: 0;
}

.page-subtitle {
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  margin-top: 0.25rem;
}

/* Rediseño de Constantes con Tarjetas */
.settings-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.setting-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  transition: border-color 0.25s, box-shadow 0.25s, transform 0.2s;
}

.setting-card:hover {
  border-color: var(--color-border-focus);
  background: rgba(184, 150, 46, 0.015);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.setting-card.card-modified {
  border-color: var(--color-warning);
  box-shadow: 0 0 12px rgba(207, 151, 61, 0.15);
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  flex: 1;
}

.setting-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.setting-title {
  font-family: var(--font-main);
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: 0.02em;
}

.badges-group {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.code-badge {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  background: rgba(201, 162, 39, 0.08);
  color: var(--color-gold);
  padding: 0.1rem 0.45rem;
  border-radius: 3px;
  border: 1px solid rgba(201, 162, 39, 0.15);
}

.badge-default {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  background: rgba(138, 135, 98, 0.12);
  color: var(--color-text-muted);
  padding: 0.1rem 0.45rem;
  border-radius: 3px;
  border: 1px solid var(--color-border);
}

.badge-custom {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  background: rgba(81, 161, 85, 0.08);
  color: #4ade80;
  border: 1px solid rgba(81, 161, 85, 0.2);
  padding: 0.1rem 0.45rem;
  border-radius: 3px;
  display: inline-flex;
  align-items: center;
}

.setting-description {
  font-family: var(--font-main);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  line-height: 1.45;
  margin: 0;
}

.setting-meta {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-dim);
  background: rgba(26, 26, 18, 0.35);
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  border: 1px dashed var(--color-border);
  align-self: flex-start;
}

.meta-icon {
  color: var(--color-text-dim);
}

.meta-label {
  color: var(--color-text-dim);
}

.meta-value {
  color: var(--color-gold);
  font-weight: 600;
}

.meta-unit {
  font-size: 0.65rem;
  color: var(--color-text-dim);
  margin-left: 0.15rem;
}

/* Controles de Acción */
.setting-action-group {
  flex-shrink: 0;
}

.input-with-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 150px;
}

.input-valor {
  width: 100%;
  text-align: left;
  font-family: var(--font-mono);
  font-size: var(--text-base);
  padding-right: 3.5rem; /* Espacio para la unidad */
}

.input-valor.modified {
  border-color: var(--color-warning);
  box-shadow: 0 0 0 2px rgba(207, 151, 61, 0.2);
}

.input-unit {
  position: absolute;
  right: 0.75rem;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  pointer-events: none;
}

.btn-save-inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.55rem 1rem;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--color-gold);
  color: #1a1a14;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 90px;
  height: 38px;
}

.btn-save-inline:hover:not(:disabled) {
  background: var(--color-gold-light);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(179, 144, 40, 0.3);
}

.btn-save-inline:active:not(:disabled) {
  transform: translateY(0);
}

.btn-save-inline:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

/* Nota Informativa */
.nota-info-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: rgba(207, 151, 61, 0.05);
  border: 1px solid rgba(207, 151, 61, 0.15);
  border-radius: var(--radius-md);
  padding: 1rem 1.25rem;
  margin-top: 1.25rem;
}

.nota-text {
  font-family: var(--font-main);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.5;
}

.warn-icon {
  color: var(--color-warning);
  flex-shrink: 0;
  margin-top: 0.1rem;
}

/* Rediseño de Telegram Premium */
.config-card-premium {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.75rem;
  max-width: 700px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.card-status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
}

.status-indicator-group {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.status-text {
  font-family: var(--font-main);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text);
}

.tg-indicator-glow {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.tg-indicator-glow.activo {
  background: #4ade80;
  box-shadow: 0 0 10px #4ade80, 0 0 4px #4ade80;
}

.tg-indicator-glow.inactivo {
  background: var(--color-text-dim);
  box-shadow: none;
}

.status-badge {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  padding: 0.2rem 0.55rem;
  border-radius: 3px;
  letter-spacing: 0.05em;
  font-weight: 700;
}

.status-badge.configured {
  background: rgba(81, 161, 85, 0.1);
  color: #4ade80;
  border: 1px solid rgba(81, 161, 85, 0.25);
}

.status-badge.unconfigured {
  background: rgba(138, 135, 98, 0.08);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}

.tg-fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-con-icono {
  padding-left: 2.5rem;
}

.input-icon {
  position: absolute;
  left: 0.85rem;
  color: var(--color-text-dim);
  pointer-events: none;
  transition: color 0.2s;
}

.field-input:focus + .input-icon {
  color: var(--color-gold);
}

.field-hint {
  font-family: var(--font-main);
  font-size: var(--text-sm);
  color: var(--color-text-faint);
  margin-top: 0.3rem;
  line-height: 1.4;
}

.link-gold {
  color: var(--color-gold);
  text-decoration: none;
  font-weight: 600;
  transition: color 0.15s;
}

.link-gold:hover {
  color: var(--color-gold-light);
  text-decoration: underline;
}

.info-alert-box {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  background: rgba(179, 144, 40, 0.04);
  border: 1px solid rgba(179, 144, 40, 0.15);
  border-radius: var(--radius-sm);
  padding: 0.75rem 1rem;
}

.info-icon {
  color: var(--color-gold);
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.info-text {
  font-family: var(--font-main);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.45;
}

.tg-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.75rem;
  flex-wrap: wrap;
}

.btn-primary-premium {
  background: var(--color-gold);
  color: #1a1a14;
  border: none;
}

.btn-secondary-premium {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.55rem 1.25rem;
  background: transparent;
  border: 1px solid var(--color-border-focus);
  border-radius: var(--radius-sm);
  color: var(--color-gold);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 38px;
}

.btn-secondary-premium:hover:not(:disabled) {
  background: var(--color-gold-bg);
  border-color: var(--color-gold);
  transform: translateY(-1px);
}

.btn-secondary-premium:active:not(:disabled) {
  transform: translateY(0);
}

.btn-secondary-premium:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

/* Responsividad */
@media (max-width: 768px) {
  .setting-card {
    flex-direction: column;
    align-items: stretch;
    gap: 1.25rem;
  }
  
  .setting-action-group {
    align-self: flex-end;
  }
  
  .input-wrapper {
    width: 100%;
    max-width: 200px;
  }
}

@media (max-width: 560px) {
  .tg-fields-grid {
    grid-template-columns: 1fr;
  }
  
  .tg-fields-grid .field-full {
    grid-column: 1;
  }
  
  .tg-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn-save-inline,
  .btn-secondary-premium {
    width: 100%;
  }
}
</style>
