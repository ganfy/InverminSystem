<template>
  <div class="page-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">Configuración del Sistema</h1>
        <p class="page-subtitle">Parámetros de cálculo y notificaciones</p>
      </div>
    </header>

    <!-- ── Sección: Constantes de Cálculo ─────────────────────────────────── -->
    <section class="config-section">
      <h2 class="section-title">Constantes de Cálculo Metalúrgico</h2>

      <div v-if="cargandoCalculo" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem" /> Cargando…
      </div>

      <div v-else class="config-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>PARÁMETRO</th>
              <th>DESCRIPCIÓN</th>
              <th class="align-right">DEFAULT</th>
              <th class="align-right" style="width:180px">VALOR ACTUAL</th>
              <th style="width:120px"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in constantes" :key="c.clave">
              <td>
                <code class="code-badge">{{ c.clave }}</code>
                <span v-if="!c.en_bd" class="badge-default">default</span>
              </td>
              <td class="text-muted">{{ c.descripcion }}</td>
              <td class="align-right text-muted">{{ c.default }}</td>
              <td class="align-right">
                <input
                  v-model="editsCalculo[c.clave]"
                  type="text"
                  class="field-input input-valor"
                  :class="{ modified: editsCalculo[c.clave] !== c.valor }"
                />
              </td>
              <td class="align-center">
                <button
                  class="btn-save"
                  :disabled="guardandoCalculo[c.clave] || editsCalculo[c.clave] === c.valor"
                  @click="guardarConstante(c.clave)"
                >
                  <span v-if="guardandoCalculo[c.clave]" class="spinner" />
                  <span v-else>Guardar</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p class="nota-info">
          ⚠ Cambios aplican desde la siguiente operación. Lotes ya liquidados no se recalculan.
          Solo Admin puede modificar.
        </p>
      </div>
    </section>

    <!-- ── Sección: Notificaciones Telegram ───────────────────────────────── -->
    <section class="config-section">
      <h2 class="section-title">Notificaciones por Telegram</h2>

      <div v-if="cargandoTelegram" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem" /> Cargando…
      </div>

      <div v-else class="telegram-card">
        <div class="tg-status">
          <span :class="['tg-indicator', telegramCfg.configurado ? 'activo' : 'inactivo']" />
          <span>{{ telegramCfg.configurado ? 'Bot configurado' : 'Sin configurar' }}</span>
        </div>

        <div class="tg-fields">
          <div v-if="!telegramCfg.desde_env" class="field-row">
            <label class="field-label">Token del Bot</label>
            <input
              v-model="editsTelegram.bot_token"
              type="password"
              class="field-input"
              placeholder="1234567890:ABCdef..."
              autocomplete="off"
            />
            <p class="field-hint">
              Obtén uno en <a href="https://t.me/BotFather" target="_blank">@BotFather</a>
            </p>
          </div>
          <div v-else class="field-row">
            <p class="field-hint" style="margin-top: 0; margin-bottom: 0.75rem; font-size: 0.9rem; line-height: 1.4;">
              El token del bot está configurado en el servidor. 
              Si necesitas crear o administrar el bot, visita <a href="https://t.me/BotFather" target="_blank">@BotFather</a>.
            </p>
          </div>

          <div class="field-row">
            <label class="field-label">Chat ID</label>
            <input
              v-model="editsTelegram.chat_id"
              type="text"
              class="field-input"
              placeholder="-100123456789 o tu user ID"
            />
            <p class="field-hint">
              Usa <a href="https://t.me/userinfobot" target="_blank">@userinfobot</a>
              para obtener tu ID, o el ID del grupo si quieres alertar a varios.
            </p>
          </div>

          <div class="field-row field-row-inline">
            <label class="field-label">Hora del resumen diario</label>
            <input
              v-model="editsTelegram.hora_resumen"
              type="time"
              class="field-input input-inline"
            />
            <span class="field-label">hs</span>
          </div>
          <p class="field-hint" style="margin-top:-0.5rem">
            Se enviará un resumen con todas las alertas activas a esta hora cada día.
          </p>
        </div>

        <div class="tg-actions">
          <button
            class="btn-save"
            :disabled="guardandoTelegram"
            @click="guardarTelegram"
          >
            <span v-if="guardandoTelegram" class="spinner" />
            <span v-else>Guardar</span>
          </button>
          <button
            class="btn-secondary"
            :disabled="!telegramCfg.configurado || probandoTelegram"
            @click="probarTelegram"
          >
            <span v-if="probandoTelegram" class="spinner" />
            <span v-else>Enviar mensaje de prueba</span>
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

const ui = useUiStore()

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
  const ok = await ui.showConfirm({
    title: 'Actualizar constante',
    message: `¿Cambiar "${clave}" a ${valor}? Afecta futuros cálculos de ley.`,
    confirmLabel: 'Actualizar',
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
  margin-bottom: 2.5rem;
}

.section-title {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  color: var(--color-text-primary);
  margin: 0 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.page-subtitle {
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  margin-top: 0.25rem;
}

/* Constantes */
.config-table-wrapper {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}

.input-valor {
  width: 130px;
  text-align: right;
  font-family: var(--font-mono);
}
.input-valor.modified {
  border-color: var(--color-gold);
  box-shadow: 0 0 0 2px rgba(201, 162, 39, 0.2);
}

.code-badge {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  background: rgba(201, 162, 39, 0.1);
  color: var(--color-gold);
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  margin-right: 0.4rem;
}
.badge-default {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  background: rgba(148, 163, 184, 0.15);
  color: var(--color-text-muted);
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
  vertical-align: middle;
}
.text-muted { color: var(--color-text-muted); }
.nota-info {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
  margin: 0;
  line-height: 1.6;
}

/* Telegram */
.telegram-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 1.5rem;
  max-width: 560px;
}

.tg-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  margin-bottom: 1.25rem;
}
.tg-indicator {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tg-indicator.activo  { background: #4ade80; box-shadow: 0 0 6px #4ade80; }
.tg-indicator.inactivo { background: var(--color-text-muted); }

.tg-fields { display: flex; flex-direction: column; gap: 1rem; }

.field-row { display: flex; flex-direction: column; gap: 0.3rem; }
.field-row-inline {
  flex-direction: row;
  align-items: center;
  gap: 0.6rem;
}
.field-row-inline .field-input { width: auto; }

.field-hint {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: 0;
}
.field-hint a { color: var(--color-gold); }

.input-inline { width: 120px; }

.tg-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-save {
  padding: 0.4rem 1.1rem;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  border: none;
  border-radius: 3px;
  background: var(--color-gold);
  color: #1a1a14;
  cursor: pointer;
  transition: background 0.15s;
  min-width: 80px;
}
.btn-save:hover:not(:disabled) { background: var(--color-gold-light); }
.btn-save:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
