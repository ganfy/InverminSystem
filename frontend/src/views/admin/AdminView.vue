<template>
  <div class="admin-page">
    <!-- ── Header ───────────────────────────────────────────────────── -->
    <header class="page-header">
      <div class="header-title-row">
        <ShieldCheck class="header-icon" :size="28" />
        <div>
          <h1 class="page-title">Administración del Sistema</h1>
          <p class="page-subtitle">Usuarios, parámetros de cálculo y notificaciones</p>
        </div>
      </div>
    </header>

    <!-- ── Tab Bar ──────────────────────────────────────────────────── -->
    <div class="tab-bar">
      <button
        v-for="tab in TABS"
        :key="tab.id"
        class="tab-btn"
        :class="{ active: tabActivo === tab.id }"
        @click="tabActivo = tab.id"
      >
        <component :is="tab.icon" :size="16" />
        <span>{{ tab.label }}</span>
        <span v-if="tab.id === 'usuarios' && usuarios.length" class="tab-badge">
          {{ usuarios.length }}
        </span>
      </button>
    </div>

    <!-- ════════════════════════════════════════════════════════════
         TAB: USUARIOS
    ════════════════════════════════════════════════════════════ -->
    <div v-show="tabActivo === 'usuarios'" class="tab-content">
      <div class="section-toolbar">
        <!-- Filtros -->
        <div class="filtros">
          <select class="field-input field-select filtro-select" v-model="filtroRol">
            <option value="">Todos los roles</option>
            <option v-for="r in ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
          </select>
          <select class="field-input field-select filtro-select" v-model="filtroEstado">
            <option value="">Todos los estados</option>
            <option value="activo">Activos</option>
            <option value="inactivo">Inactivos</option>
          </select>
          <input
            class="field-input filtro-search"
            v-model="busqueda"
            placeholder="Buscar nombre, usuario..."
          />
        </div>
        <button class="btn-primary ready btn-con-icono" @click="abrirCrear">
          <UserPlus :size="16" />
          Nuevo usuario
        </button>
      </div>

      <!-- Tabla -->
      <div class="tabla-wrapper">
        <div v-if="cargandoUsuarios" class="estado-tabla">
          <span class="spinner" style="margin-right:0.5rem" /> Cargando usuarios…
        </div>
        <div v-else-if="errorUsuarios" class="estado-tabla error-msg">{{ errorUsuarios }}</div>
        <table v-else class="tabla">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Usuario</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Creado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="usuariosFiltrados.length === 0">
              <td colspan="6" class="sin-datos">Sin resultados</td>
            </tr>
            <tr v-for="u in usuariosFiltrados" :key="u.id" :class="{ inactivo: !u.activo }">
              <td class="td-nombre">{{ u.nombre_completo }}</td>
              <td class="td-mono">{{ u.username }}</td>
              <td><span class="badge-rol" :class="rolClass(u.rol)">{{ getRolLabel(u.rol) }}</span></td>
              <td>
                <span class="badge-estado" :class="u.activo ? 'activo' : 'inactivo'">
                  {{ u.activo ? 'ACTIVO' : 'INACTIVO' }}
                </span>
              </td>
              <td class="td-fecha">{{ formatFecha(u.creado_en) }}</td>
              <td class="td-acciones">
                <button class="btn-icon" title="Editar" @click="abrirEditar(u)">
                  <Pencil :size="16" />
                </button>
                <button
                  class="btn-icon"
                  :title="u.activo ? 'Desactivar' : 'Activar'"
                  @click="toggleEstado(u)"
                >
                  <UserRoundMinus v-if="u.activo" :size="15" />
                  <UserRoundPlus v-else :size="15" />
                </button>
                <button class="btn-icon" title="Reset contraseña" @click="abrirReset(u)">
                  <KeyRound :size="16" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-show="tabActivo === 'parametros'" class="tab-content">
      <div v-if="cargandoCalculo" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem" /> Cargando parámetros…
      </div>

      <div v-else class="parametros-layout">
        <!-- Sidebar de Categorías -->
        <aside class="parametros-sidebar">
          <button
            v-for="cat in PARAM_CATEGORIES"
            :key="cat.id"
            class="param-category-btn"
            :class="{ active: currentParamCategory === cat.id }"
            @click="currentParamCategory = cat.id"
          >
            <component :is="cat.icon" :size="16" class="cat-icon" />
            <span>{{ cat.name }}</span>
          </button>
        </aside>

        <!-- Panel de Configuración -->
        <div class="parametros-panel">
          <div class="category-header-row-param">
            <component :is="activeCategoryDetails.icon" :size="20" class="category-header-icon" />
            <h2 class="category-header-title">{{ activeCategoryDetails.name }}</h2>
          </div>

          <!-- Aviso contextual para la categoría de numeración -->
          <div v-if="currentParamCategory === 'numeracion'" class="nota-info-card" style="margin-bottom: 1.25rem; background: rgba(207,151,61,0.07); border-color: rgba(207,151,61,0.3);">
            <AlertTriangle :size="16" class="warn-icon" />
            <p class="nota-text">
              <strong>Numeración de IPs y Tickets:</strong>
              <br/>• <code>proximo_ip</code>: define el número mínimo desde el que se generarán nuevos IPs de lote
              (tanto online como en bloques offline). El sistema usa el mayor entre este valor y el máximo ya registrado.
              <br/>• <code>proximo_ticket</code>: define el inicio del próximo bloque de tickets reservados para dispositivos sin conexión.
              <br/>El sistema valida que el valor nuevo no esté ya registrado. Usa esto para <em>saltar</em> la numeración en producción (p. ej. tras importar datos o reiniciar el año).
            </p>
          </div>

          <!-- Aviso contextual para Pruebas Metalúrgicas -->
          <div v-if="currentParamCategory === 'pruebas'" class="nota-info-card" style="margin-bottom: 1.25rem; background: rgba(207,151,61,0.07); border-color: rgba(207,151,61,0.3);">
            <FlaskConical :size="16" class="warn-icon" />
            <p class="nota-text">
              <strong>Modo de Identificación de Muestras (<code>pruebas_usa_cip</code>):</strong>
              <br/>• <strong>CIP Ofuscado (true):</strong> genera códigos alfanuméricos (ej. <code>CIP-058598D-R1</code>) para ocultar el IP del lote ante laboratorios externos.
              <br/>• <strong>Solo IP (false):</strong> usa el número de IP directo con sufijo (ej. <code>IP-0042-R1</code>) para laboratorios internos que ya conocen el lote.
            </p>
          </div>

          <div class="settings-grid">
            <div
              v-for="c in filteredConstantes"
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
                <div class="setting-meta" v-if="c.clave !== 'labs_lista'">
                  <Info :size="12" class="meta-icon" />
                  <span class="meta-label">Valor por defecto:</span>
                  <span class="meta-value">
                    {{ c.default }}
                    <span class="meta-unit" v-if="UNIDADES[c.clave]">{{ UNIDADES[c.clave] }}</span>
                  </span>
                </div>
              </div>

              <div class="setting-action-group">
                <div class="field">
                  <label class="field-label">Valor Actual</label>
                  <div class="input-with-button">
                    <div class="input-wrapper">
                      <!-- Dropdown para Unidades -->
                      <select
                        v-if="c.clave.startsWith('unidad_')"
                        v-model="editsCalculo[c.clave]"
                        class="field-input field-select select-valor"
                        :class="{ modified: editsCalculo[c.clave] !== c.valor }"
                      >
                        <option value="TM">TM (Tonelada Métrica)</option>
                        <option value="TMC">TMC (Tonelada Corta)</option>
                        <option value="KG">KG (Kilogramo)</option>
                      </select>

                      <!-- Dropdown para Modos de Redondeo -->
                      <select
                        v-else-if="c.clave.startsWith('redondeo_ley_')"
                        v-model="editsCalculo[c.clave]"
                        class="field-input field-select select-valor"
                        :class="{ modified: editsCalculo[c.clave] !== c.valor }"
                      >
                        <option value="normal">Normal / Matemático (.5 sube)</option>
                        <option value="abajo">Hacia Abajo (Truncar)</option>
                        <option value="arriba">Hacia Arriba</option>
                        <option value="bancario">Bancario / Par (.5 par)</option>
                      </select>

                      <!-- Dropdown para Modo de Identificación Pruebas -->
                      <select
                        v-else-if="c.clave === 'pruebas_usa_cip'"
                        v-model="editsCalculo[c.clave]"
                        class="field-input field-select select-valor"
                        :class="{ modified: editsCalculo[c.clave] !== c.valor }"
                      >
                        <option value="true">CIP Ofuscado (CIP-XXXX-R1)</option>
                        <option value="false">Solo IP Lote (IP-XXXX-R1)</option>
                      </select>

                      <!-- Textarea para listas JSON -->
                      <textarea
                        v-else-if="c.clave === 'labs_lista'"
                        v-model="editsCalculo[c.clave]"
                        class="field-input input-valor"
                        :class="{ modified: editsCalculo[c.clave] !== c.valor }"
                        rows="4"
                        style="resize: vertical; min-height: 80px;"
                      ></textarea>

                      <!-- Inputs estándar para otros valores -->
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
        </div>
      </div>

      <div class="nota-info-card">
        <AlertTriangle :size="16" class="warn-icon" />
        <p class="nota-text">
          <strong>Aviso de recálculo:</strong> Los cambios aplicarán a partir de la siguiente
          operación registrada. Los lotes ya liquidados no se verán afectados.
          Modificaciones restringidas a administradores.
        </p>
      </div>
    </div>
    <div v-show="tabActivo === 'notificaciones'" class="tab-content">
      <div v-if="cargandoTelegram" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem" /> Cargando configuración…
      </div>

      <div v-else class="config-card-premium">
        <div class="card-status-header">
          <div class="status-indicator-group">
            <span :class="['tg-indicator-glow', telegramCfg.configurado ? 'activo' : 'inactivo']" />
            <span class="status-text">
              {{ telegramCfg.configurado ? 'Servicio de Notificaciones Activo' : 'Servicio Desconfigurado' }}
            </span>
          </div>
          <span class="status-badge" :class="telegramCfg.configurado ? 'configured' : 'unconfigured'">
            {{ telegramCfg.configurado ? 'Conectado' : 'Sin conexión' }}
          </span>
        </div>

        <div class="notif-channels">
          <div class="channel-header">
            <Bot :size="16" class="channel-icon" />
            <span class="channel-label">Canal: Telegram</span>
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
                Obtén un token creando un bot con
                <a href="https://t.me/BotFather" target="_blank" class="link-gold">@BotFather</a>.
              </p>
            </div>
            <div v-else class="field field-full">
              <div class="info-alert-box">
                <Info :size="16" class="info-icon" />
                <p class="info-text">
                  El token del bot está configurado en las variables de entorno del servidor.
                  Si necesitas cambiarlo, contacta al administrador del sistema.
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
                Usa <a href="https://t.me/userinfobot" target="_blank" class="link-gold">@userinfobot</a>
                para obtener tu ID personal, o el ID de tu canal/grupo.
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

      <!-- Placeholder para futuros canales -->
      <div class="future-channels">
        <div class="future-badge">
          <Mail :size="14" />
          <span>Notificaciones por correo — próximamente</span>
        </div>
      </div>
    </div>

    <!-- ── Modal crear/editar usuario ───────────────────────────────── -->
    <div v-if="modalVisible" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ modoEditar ? 'Editar usuario' : 'Nuevo usuario' }}</h2>
          <button class="btn-cerrar" @click="cerrarModal"><X :size="18" /></button>
        </div>

        <div class="modal-body">
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Nombre completo *</label>
              <input class="field-input" v-model="form.nombre_completo" placeholder="Nombre completo" />
            </div>
            <div class="field">
              <label class="field-label">Usuario *</label>
              <input
                class="field-input"
                v-model="form.username"
                placeholder="username"
                :disabled="modoEditar"
                :class="{ disabled: modoEditar }"
              />
            </div>
            <div class="field">
              <label class="field-label">Rol *</label>
              <select class="field-input field-select" v-model="form.rol">
                <option value="" disabled>Seleccionar rol</option>
                <option v-for="r in ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Email</label>
              <input class="field-input" v-model="form.email" placeholder="email@ejemplo.com" type="email" />
            </div>
            <div v-if="!modoEditar" class="field field-full">
              <label class="field-label">Contraseña *</label>
              <input class="field-input" v-model="form.password" placeholder="Contraseña inicial" type="password" />
            </div>
          </div>
          <p v-if="formError" class="error-msg">{{ formError }}</p>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="cerrarModal">Cancelar</button>
          <button class="btn-primary" :disabled="guardandoUsuario" @click="guardarUsuario">
            {{ guardandoUsuario ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Modal reset password ──────────────────────────────────────── -->
    <div v-if="resetVisible" class="modal-overlay" @click.self="resetVisible = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Reset contraseña</h2>
          <button class="btn-cerrar" @click="resetVisible = false"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <p class="reset-usuario">Usuario: <strong>{{ usuarioReset?.username }}</strong></p>
          <div class="field">
            <label class="field-label">Nueva contraseña *</label>
            <input class="field-input" v-model="nuevaPassword" type="password" placeholder="Nueva contraseña" />
          </div>
          <p v-if="resetError" class="error-msg">{{ resetError }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="resetVisible = false">Cancelar</button>
          <button class="btn-primary" :disabled="guardandoUsuario" @click="confirmarReset">
            {{ guardandoUsuario ? 'Guardando...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { usuariosApi, type UsuarioListItem } from '@/api/usuarios'
import { adminApi, type ConstanteCalculo } from '@/api/admin'
import { useUiStore } from '@/stores/ui'
import {
  ShieldCheck, Users, Settings, BellRing,
  Pencil, KeyRound, X,
  Database, Info, AlertTriangle, Save,
  Bot, MessageSquare, Clock, Send, Mail,
  Scale, FlaskConical, Microscope, Beaker,
  UserPlus, UserRoundMinus, UserRoundPlus,
} from 'lucide-vue-next'

const ui = useUiStore()

// ── Tabs ─────────────────────────────────────────────────────────────────────
const TABS: { id: 'usuarios' | 'parametros' | 'notificaciones'; label: string; icon: any }[] = [
  { id: 'usuarios',       label: 'Usuarios',       icon: Users    },
  { id: 'parametros',     label: 'Parámetros',     icon: Settings },
  { id: 'notificaciones', label: 'Notificaciones', icon: BellRing },
]

// Permite llegar al tab correcto desde una URL si se quiere en el futuro
const tabActivo = ref<'usuarios' | 'parametros' | 'notificaciones'>('usuarios')

// ── Datos estáticos ───────────────────────────────────────────────────────────
const ROLES = [
  { value: 'Admin', label: 'Admin' },
  { value: 'Gerencia', label: 'Gerencia' },
  { value: 'Comercial', label: 'Comercial' },
  { value: 'Laboratorista', label: 'Laboratorista' },
  { value: 'OperadorBalanza', label: 'Operador Balanza' },
  { value: 'TecnicoMuestreo', label: 'Técnico Muestreo' },
  { value: 'Metalurgista', label: 'Metalurgista' },
]

const NOMBRES_AMIGABLES: Record<string, string> = {
  // Empresa
  empresa_nombre: 'Razón Social / Nombre',
  empresa_planta: 'Nombre de la Planta',
  empresa_ruc: 'RUC de la Empresa',
  empresa_direccion: 'Dirección de la Empresa',

  // Unidades
  unidad_balanza: 'Unidad de Módulo Balanza',
  unidad_muestreo: 'Unidad de Módulo Muestreo',
  unidad_laboratorio: 'Unidad de Módulo Laboratorio',
  unidad_liquidaciones: 'Unidad de Módulo Liquidaciones',
  unidad_default: 'Unidad por Defecto',

  // Cálculo
  factor_oz_tc: 'Factor de Conversión (Oz/TC → Gr/TM)',
  blank_correction_ag: 'Corrección en Blanco de Plata (Ag)',
  umbral_volado_oz_tc: 'Umbral de Ley para Lote Volado',
  costo_fijo_planta_maquila: 'Costo Fijo Planta para Maquila',
  decimales_ley_laboratorio: 'Decimales Ley Laboratorio',
  decimales_ley_planta: 'Decimales Ley Planta',
  decimales_ley_comercial: 'Decimales Ley Comercial',
  decimales_ley_final: 'Decimales Ley Final',
  redondeo_ley_laboratorio: 'Redondeo Ley Laboratorio',
  redondeo_ley_planta: 'Redondeo Ley Planta',
  redondeo_ley_comercial: 'Redondeo Ley Comercial',
  redondeo_ley_final: 'Redondeo Ley Final',

  // Muestreo
  MUESTREO_MAX_INTENTOS: 'Intentos Máximos de Muestreo',
  MUESTREO_HUMEDAD_MAX_PCT: 'Humedad Máxima Permitida',
  MUESTREO_MALLA_MIN_PCT: 'Malla Mínima Aceptable',
  MUESTREO_MALLA_MAX_PCT: 'Malla Máxima Aceptable',
  MAX_CIPS_GENERADOS: 'Cantidad Máxima de CIPs a Generar',
  MUESTREO_CIPS_IMPRIMIR: 'Cantidad de CIPs a Imprimir (Etiquetas)',
  labs_lista: 'Lista de Laboratorios Externos',

  // Laboratorio
  LAB_DIFERENCIA_PLANTA_MINERO: 'Diferencia Máxima entre Labs / Planta vs Minero',

  // Pruebas
  CAMPANA_META_ORO_FINO_DEFAULT: 'Meta de Oro Fino por Campaña',
  sla_metalurgia_horas: 'SLA Retraso en Pruebas Metalúrgicas',
  sla_limite_plazo_horas: 'SLA Plazo Límite en Pruebas Metalúrgicas',
  pruebas_usa_cip: 'Modo de Identificación de Muestras (CIP vs IP)',
  pruebas_umbral_recup_alta: 'Umbral Alta Recuperación',
  pruebas_umbral_recup_baja: 'Umbral Baja Recuperación (Reensayo)',

  // Alertas
  alerta_horas_pesado_muestreo: 'SLA Pesado a Muestreo',
  alerta_horas_muestreo_ley: 'SLA Muestreo a Ley',
  alerta_horas_ley_recuperacion: 'SLA Ley a Recuperación',
  alerta_dias_volado_stock: 'SLA Lote Volado en Stock sin Ruma',

  // Balanza offline
  proximo_ticket: 'Próximo Número de Ticket',
  tamano_bloque_ticket: 'Tamaño de Bloque de Tickets Offline',
  proximo_ip: 'Próximo Número de IP de Lote',
  tamano_bloque_ip: 'Tamaño de Bloque de IPs Offline',
}

const UNIDADES: Record<string, string> = {
  factor_oz_tc: 'Gr/TM',
  blank_correction_ag: 'mg',
  umbral_volado_oz_tc: 'Oz/TC',
  costo_fijo_planta_maquila: 'USD/TM',
  MUESTREO_HUMEDAD_MAX_PCT: '%',
  MUESTREO_MALLA_MIN_PCT: '%',
  MUESTREO_MALLA_MAX_PCT: '%',
  LAB_DIFERENCIA_PLANTA_MINERO: 'Oz/TC',
  CAMPANA_META_ORO_FINO_DEFAULT: 'g',
  sla_metalurgia_horas: 'horas',
  sla_limite_plazo_horas: 'horas',
  pruebas_umbral_recup_alta: '%',
  pruebas_umbral_recup_baja: '%',
  alerta_horas_pesado_muestreo: 'horas',
  alerta_horas_muestreo_ley: 'horas',
  alerta_horas_ley_recuperacion: 'horas',
  alerta_dias_volado_stock: 'días',
}

const PARAM_CATEGORIES = [
  {
    id: 'empresa',
    name: 'Empresa y Planta',
    icon: ShieldCheck,
    keys: ['empresa_nombre', 'empresa_planta', 'empresa_ruc', 'empresa_direccion']
  },
  {
    id: 'unidades',
    name: 'Unidades de Peso por Módulo',
    icon: Scale,
    keys: ['unidad_balanza', 'unidad_muestreo', 'unidad_laboratorio', 'unidad_liquidaciones', 'unidad_default']
  },
  {
    id: 'calculo',
    name: 'Constantes de Cálculo Metalúrgico',
    icon: Database,
    keys: ['factor_oz_tc', 'blank_correction_ag', 'umbral_volado_oz_tc', 'costo_fijo_planta_maquila', 'decimales_ley_laboratorio', 'decimales_ley_planta', 'decimales_ley_comercial', 'decimales_ley_final', 'redondeo_ley_laboratorio', 'redondeo_ley_planta', 'redondeo_ley_comercial', 'redondeo_ley_final']
  },
  {
    id: 'muestreo',
    name: 'Muestreo y CIPs',
    icon: FlaskConical,
    keys: ['MUESTREO_MAX_INTENTOS', 'MUESTREO_HUMEDAD_MAX_PCT', 'MUESTREO_MALLA_MIN_PCT', 'MUESTREO_MALLA_MAX_PCT', 'MAX_CIPS_GENERADOS', 'MUESTREO_CIPS_IMPRIMIR', 'labs_lista']
  },
  {
    id: 'laboratorio',
    name: 'Laboratorio y Calidad',
    icon: Microscope,
    keys: ['LAB_DIFERENCIA_PLANTA_MINERO']
  },
  {
    id: 'pruebas',
    name: 'Pruebas Metalúrgicas y Campañas',
    icon: Beaker,
    keys: ['CAMPANA_META_ORO_FINO_DEFAULT', 'sla_metalurgia_horas', 'sla_limite_plazo_horas', 'pruebas_usa_cip', 'pruebas_umbral_recup_alta', 'pruebas_umbral_recup_baja']
  },
  {
    id: 'alertas',
    name: 'SLA y Alertas de Tiempos (Dashboard)',
    icon: BellRing,
    keys: ['alerta_horas_pesado_muestreo', 'alerta_horas_muestreo_ley', 'alerta_horas_ley_recuperacion', 'alerta_dias_volado_stock']
  },
  {
    id: 'numeracion',
    name: 'Numeración Balanza (Tickets e IPs)',
    icon: Scale,
    keys: ['proximo_ticket', 'tamano_bloque_ticket', 'proximo_ip', 'tamano_bloque_ip']
  }
]

// ══════════════════════════════════════════════════════════════════════════════
// USUARIOS
// ══════════════════════════════════════════════════════════════════════════════
const usuarios        = ref<UsuarioListItem[]>([])
const cargandoUsuarios = ref(false)
const errorUsuarios    = ref('')

const filtroRol    = ref('')
const filtroEstado = ref('')
const busqueda     = ref('')

const modalVisible   = ref(false)
const modoEditar     = ref(false)
const guardandoUsuario = ref(false)
const formError      = ref('')
const editandoId     = ref<number | null>(null)

const form = ref({
  nombre_completo: '',
  username: '',
  rol: '',
  email: '',
  password: '',
})

const resetVisible  = ref(false)
const usuarioReset  = ref<UsuarioListItem | null>(null)
const nuevaPassword = ref('')
const resetError    = ref('')

const usuariosFiltrados = computed(() => {
  return usuarios.value.filter(u => {
    if (filtroRol.value && u.rol !== filtroRol.value) return false
    if (filtroEstado.value === 'activo'   && !u.activo) return false
    if (filtroEstado.value === 'inactivo' &&  u.activo) return false
    if (busqueda.value) {
      const q = busqueda.value.toLowerCase()
      return u.nombre_completo.toLowerCase().includes(q) ||
             u.username.toLowerCase().includes(q)
    }
    return true
  })
})

function formatFecha(iso: string | null | undefined) {
  if (!iso) return 'N/A'
  const utc = (iso.includes('+') || iso.endsWith('Z')) ? iso : iso + 'Z'
  return new Date(utc).toLocaleString('es-PE', {
    timeZone: 'America/Lima',
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function getRolLabel(rolCodigo: string) {
  const r = ROLES.find(x => x.value === rolCodigo)
  return r ? r.label : rolCodigo
}

function rolClass(rolCodigo: string) {
  const map: Record<string, string> = {
    'Admin':            'rol-admin',
    'Gerencia':         'rol-gerencia',
    'Comercial':        'rol-comercial',
    'Laboratorista':    'rol-lab',
    'OperadorBalanza':  'rol-operador',
    'TecnicoMuestreo':  'rol-tecnico',
    'Metalurgista':     'rol-metalurgista',
  }
  return map[rolCodigo] ?? ''
}

async function cargarUsuarios() {
  cargandoUsuarios.value = true
  errorUsuarios.value = ''
  try {
    usuarios.value = await usuariosApi.listar()
  } catch {
    errorUsuarios.value = 'Error al cargar usuarios'
  } finally {
    cargandoUsuarios.value = false
  }
}

function abrirCrear() {
  modoEditar.value = false
  editandoId.value = null
  form.value = { nombre_completo: '', username: '', rol: '', email: '', password: '' }
  formError.value = ''
  modalVisible.value = true
}

function abrirEditar(u: UsuarioListItem) {
  modoEditar.value = true
  editandoId.value = u.id
  form.value = {
    nombre_completo: u.nombre_completo,
    username: u.username,
    rol: u.rol,
    email: u.email ?? '',
    password: '',
  }
  formError.value = ''
  modalVisible.value = true
}

function cerrarModal() { modalVisible.value = false }

async function guardarUsuario() {
  formError.value = ''
  if (!form.value.nombre_completo || !form.value.rol) {
    formError.value = 'Nombre y rol son obligatorios'
    return
  }
  if (!modoEditar.value && (!form.value.username || !form.value.password)) {
    formError.value = 'Usuario y contraseña son obligatorios'
    return
  }
  guardandoUsuario.value = true
  try {
    if (modoEditar.value && editandoId.value) {
      await usuariosApi.editar(editandoId.value, {
        nombre_completo: form.value.nombre_completo,
        rol_codigo: form.value.rol,
        email: form.value.email || undefined,
      })
    } else {
      await usuariosApi.crear({
        username:        form.value.username,
        password:        form.value.password,
        nombre_completo: form.value.nombre_completo,
        rol_codigo:      form.value.rol,
        email:           form.value.email || undefined,
      })
    }
    cerrarModal()
    await cargarUsuarios()
    ui.toast(modoEditar.value ? 'Usuario actualizado' : 'Usuario creado', 'success')
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al guardar', 'error')
  } finally {
    guardandoUsuario.value = false
  }
}

async function toggleEstado(u: UsuarioListItem) {
  const ok = await ui.showConfirm({
    title:        u.activo ? 'Desactivar usuario' : 'Activar usuario',
    message:      u.activo
      ? `¿Desactivar a ${u.nombre_completo}? No podrá ingresar al sistema.`
      : `¿Reactivar acceso de ${u.nombre_completo}?`,
    confirmLabel: u.activo ? 'Desactivar' : 'Activar',
    danger:       u.activo,
  })
  if (!ok) return
  try {
    if (u.activo) {
      await usuariosApi.desactivar(u.id)
      ui.toast(`${u.nombre_completo} desactivado`, 'warning')
    } else {
      await usuariosApi.activar(u.id)
      ui.toast(`${u.nombre_completo} activado`, 'success')
    }
    await cargarUsuarios()
  } catch {
    ui.toast('Error al cambiar estado', 'error')
  }
}

function abrirReset(u: UsuarioListItem) {
  usuarioReset.value = u
  nuevaPassword.value = ''
  resetError.value = ''
  resetVisible.value = true
}

async function confirmarReset() {
  if (!nuevaPassword.value || nuevaPassword.value.length < 6) {
    resetError.value = 'Mínimo 6 caracteres'
    return
  }
  guardandoUsuario.value = true
  try {
    await usuariosApi.resetPassword(usuarioReset.value!.id, nuevaPassword.value)
    resetVisible.value = false
    ui.toast('Contraseña actualizada', 'success')
  } catch {
    resetError.value = 'Error al cambiar contraseña'
    ui.toast('Error al cambiar contraseña', 'error')
  } finally {
    guardandoUsuario.value = false
  }
}

// ── PARÁMETROS DE CONFIGURACIÓN ──────────────────────────────────────────────
const cargandoCalculo  = ref(true)
const constantes       = ref<ConstanteCalculo[]>([])
const editsCalculo     = reactive<Record<string, string>>({})
const guardandoCalculo = reactive<Record<string, boolean>>({})

const currentParamCategory = ref('empresa')

const activeCategoryDetails = computed(() => {
  return PARAM_CATEGORIES.find(cat => cat.id === currentParamCategory.value) ?? PARAM_CATEGORIES[0]!
})

const filteredConstantes = computed(() => {
  const activeKeys = activeCategoryDetails.value.keys
  return constantes.value.filter(c => activeKeys.includes(c.clave))
})

async function cargarConstantes() {
  cargandoCalculo.value = true
  try {
    constantes.value = await adminApi.getConstantesCalculo()
    for (const c of constantes.value) editsCalculo[c.clave] = c.valor
  } catch {
    ui.toast('Error al cargar parámetros', 'error')
  } finally {
    cargandoCalculo.value = false
  }
}

async function guardarConstante(clave: string) {
  const valor = editsCalculo[clave]?.trim()
  if (valor === undefined || valor === null) return
  const ok = await ui.showConfirm({
    title: 'Actualizar parámetro',
    message: `¿Cambiar "${NOMBRES_AMIGABLES[clave] || clave}" a "${valor}"?`,
    confirmLabel: 'Actualizar',
  })
  if (!ok) return
  guardandoCalculo[clave] = true
  try {
    await adminApi.updateConstante(clave, valor)
    ui.toast('Parámetro actualizado', 'success')
    await cargarConstantes()

    // Si se actualizó una unidad o factor_oz_tc o pruebas_usa_cip, actualizamos la config pública
    if (clave.startsWith('unidad_') || clave === 'factor_oz_tc' || clave === 'pruebas_usa_cip') {
      const publicConfig = await adminApi.getPublicConfig()
      const { updateUnidadesModulos } = await import('@/utils/units')
      updateUnidadesModulos(publicConfig)
      localStorage.setItem('public_config_cache', JSON.stringify(publicConfig))
    }
  } catch (err: any) {
    ui.toast(err?.response?.data?.detail ?? 'Error al guardar', 'error')
  } finally {
    guardandoCalculo[clave] = false
  }
}

// ── NOTIFICACIONES (Telegram) ────────────────────────────────────────────────
const cargandoTelegram  = ref(true)
const guardandoTelegram = ref(false)
const probandoTelegram  = ref(false)

interface TelegramCfg {
  bot_token: string; chat_id: string; hora_resumen: string
  configurado: boolean; desde_env?: boolean
}
const telegramCfg   = ref<TelegramCfg>({ bot_token: '', chat_id: '', hora_resumen: '07:00', configurado: false })
const editsTelegram = reactive({ bot_token: '', chat_id: '', hora_resumen: '07:00' })

async function cargarTelegram() {
  cargandoTelegram.value = true
  try {
    const cfg = await adminApi.getTelegramConfig()
    telegramCfg.value = cfg
    editsTelegram.chat_id      = cfg.chat_id
    editsTelegram.hora_resumen = cfg.hora_resumen || '07:00'
    editsTelegram.bot_token    = ''
  } catch {
    ui.toast('Error al cargar configuración de notificaciones', 'error')
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
    await adminApi.updateTelegramConfig({
      bot_token:    editsTelegram.bot_token || '(mantener)',
      chat_id:      editsTelegram.chat_id,
      hora_resumen: editsTelegram.hora_resumen,
    })
    ui.toast('Configuración guardada', 'success')
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

// ── Mount ─────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([cargarUsuarios(), cargarConstantes(), cargarTelegram()])
})
</script>

<style scoped>
/* ── Layout ─────────────────────────────────────────────────── */
.admin-page {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  color: var(--color-gold);
}

.page-subtitle {
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  margin-top: 0.25rem;
}

/* ── Tab Bar ─────────────────────────────────────────────────── */
.tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1.75rem;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.7rem 1.4rem;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s;
  position: relative;
  top: 1px;
}

.tab-btn:hover {
  color: var(--color-text);
}

.tab-btn.active {
  color: var(--color-gold);
  border-bottom-color: var(--color-gold);
}

.tab-badge {
  background: rgba(201, 162, 39, 0.15);
  color: var(--color-gold);
  border-radius: 10px;
  font-size: 0.65rem;
  padding: 0.05rem 0.45rem;
  font-weight: 700;
  margin-left: 0.1rem;
}

/* ── Tab Content ─────────────────────────────────────────────── */
.tab-content {
  animation: fadeIn 0.18s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Toolbar Usuarios ────────────────────────────────────────── */
.section-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.filtros {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  flex: 1;
}

.filtro-select  { width: 180px; }
.filtro-search  { flex: 1; min-width: 200px; }
.field-input.disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Parámetros de Cálculo ───────────────────────────────────── */
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
  transition: border-color 0.25s, box-shadow 0.25s;
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
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--color-text);
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

.meta-icon  { color: var(--color-text-dim); }
.meta-label { color: var(--color-text-dim); }
.meta-value { color: var(--color-gold); font-weight: 600; }
.meta-unit  { font-size: 0.65rem; color: var(--color-text-dim); margin-left: 0.15rem; }

.setting-action-group { flex-shrink: 0; }

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
  font-family: var(--font-mono);
  font-size: var(--text-base);
  padding-right: 3.5rem;
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

.btn-save-inline:disabled { opacity: 0.35; cursor: not-allowed; }

.btn-content { display: flex; align-items: center; gap: 0.4rem; }

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
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.5;
}

.warn-icon { color: var(--color-warning); flex-shrink: 0; margin-top: 0.1rem; }

/* ── Notificaciones ──────────────────────────────────────────── */
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
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text);
}

.tg-indicator-glow {
  width: 8px; height: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.tg-indicator-glow.activo  { background: #4ade80; box-shadow: 0 0 10px #4ade80, 0 0 4px #4ade80; }
.tg-indicator-glow.inactivo { background: var(--color-text-dim); }

.status-badge {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  padding: 0.2rem 0.55rem;
  border-radius: 3px;
  letter-spacing: 0.05em;
  font-weight: 700;
}

.status-badge.configured   { background: rgba(81,161,85,0.1); color: #4ade80; border: 1px solid rgba(81,161,85,0.25); }
.status-badge.unconfigured { background: rgba(138,135,98,0.08); color: var(--color-text-muted); border: 1px solid var(--color-border); }

.notif-channels { margin-bottom: 1.5rem; }

.channel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px dashed var(--color-border);
}

.channel-icon  { color: var(--color-gold); }
.channel-label { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-muted); font-weight: 600; }

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

.input-con-icono { padding-left: 2.5rem; }

.input-icon {
  position: absolute;
  left: 0.85rem;
  color: var(--color-text-dim);
  pointer-events: none;
  transition: color 0.2s;
}

.field-hint {
  font-size: var(--text-sm);
  color: var(--color-text-faint);
  margin-top: 0.3rem;
  line-height: 1.4;
}

.link-gold {
  color: var(--color-gold);
  text-decoration: none;
  font-weight: 600;
}
.link-gold:hover { color: var(--color-gold-light); text-decoration: underline; }

.info-alert-box {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  background: rgba(179, 144, 40, 0.04);
  border: 1px solid rgba(179, 144, 40, 0.15);
  border-radius: var(--radius-sm);
  padding: 0.75rem 1rem;
}

.info-icon  { color: var(--color-gold); flex-shrink: 0; margin-top: 0.1rem; }
.info-text  { font-size: var(--text-sm); color: var(--color-text-muted); margin: 0; line-height: 1.45; }

.tg-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-primary-premium  { background: var(--color-gold); color: #1a1a14; border: none; }

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

.btn-secondary-premium:disabled { opacity: 0.35; cursor: not-allowed; }

/* Placeholder futuros canales */
.future-channels {
  margin-top: 1.25rem;
  max-width: 700px;
}

.future-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(138, 135, 98, 0.06);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.5rem 1rem;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-dim);
}

/* ── Modal helpers ───────────────────────────────────────────── */
.reset-usuario {
  color: var(--color-text-muted);
  margin-bottom: 1rem;
  font-size: var(--text-base);
}

.reset-usuario strong { color: var(--color-text); }

/* ── Layout de Parámetros Categorizados ────────────────────────── */
.parametros-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.parametros-sidebar {
  width: 250px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.75rem;
}

.param-category-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.param-category-btn:hover {
  color: var(--color-text);
  background: rgba(201, 162, 39, 0.04);
}

.param-category-btn.active {
  color: var(--color-gold);
  background: rgba(201, 162, 39, 0.08);
  border-left: 3px solid var(--color-gold);
  padding-left: calc(1rem - 3px);
}

.cat-icon {
  flex-shrink: 0;
}

.parametros-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.category-header-row-param {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.5rem;
}

.category-header-icon {
  color: var(--color-gold);
}

.category-header-title {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  color: var(--color-text-primary);
  margin: 0;
}

.select-valor {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23c9a227' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1rem;
  padding-right: 2.5rem !important;
}

/* Responsividad adicional para el layout de parámetros */
@media (max-width: 900px) {
  .parametros-layout {
    flex-direction: column;
    align-items: stretch;
    gap: 1.5rem;
  }

  .parametros-sidebar {
    width: 100%;
    flex-direction: row;
    overflow-x: auto;
    gap: 0.5rem;
    white-space: nowrap;
    padding: 0.5rem;
  }

  .param-category-btn {
    padding: 0.5rem 1rem;
  }

  .param-category-btn.active {
    border-left: none;
    border-bottom: 2px solid var(--color-gold);
    padding-left: 1rem;
    padding-bottom: calc(0.5rem - 2px);
  }
}

/* ── Responsividad ───────────────────────────────────────────── */
@media (max-width: 768px) {
  .setting-card {
    flex-direction: column;
    align-items: stretch;
    gap: 1.25rem;
  }

  .setting-action-group { align-self: flex-end; }
  .input-wrapper { width: 100%; max-width: 200px; }
}

@media (max-width: 560px) {
  .tab-btn { padding: 0.6rem 0.9rem; font-size: 0.75rem; }
  .tg-fields-grid { grid-template-columns: 1fr; }
  .tg-actions { flex-direction: column; align-items: stretch; }

  .btn-save-inline,
  .btn-secondary-premium { width: 100%; }
}
</style>
