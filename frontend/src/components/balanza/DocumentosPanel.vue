<template>
    <section class="documentos-panel">
      <div class="panel-header">
        <h3 class="panel-title">📎 Documentos de ingreso</h3>
        <span v-if="archivosLocales.length" class="doc-count">
          {{ archivosLocales.length }} archivo(s)
        </span>
        <span v-else-if="documentosServidor.length" class="doc-count">
          {{ documentosServidor.length }} archivo(s)
        </span>
      </div>

      <!-- ── Aviso modo pre-sesión ────────────────────────────────────────────── -->
      <div v-if="!sesionId" class="aviso-presion">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 20 20" aria-hidden="true" style="vertical-align: middle;">
          <circle cx="10" cy="10" r="9" stroke="#0ea5e9" stroke-width="2" fill="#e0f2fe"/>
          <rect x="9" y="8" width="2" height="6" rx="1" fill="#0ea5e9"/>
          <rect x="9" y="5" width="2" height="2" rx="1" fill="#0ea5e9"/>
        </svg>
        <p>
          Sube los documentos del camión (GRR, GRT, licencia). Puedes subir un PDF
          con múltiples páginas o archivos separados. Luego extrae los datos para
          pre-llenar el formulario y edítalos si es necesario.
        </p>
      </div>

      <!-- ── Upload zone ───────────────────────────────────────────────────────── -->
      <div
        class="upload-zone"
        :class="{ 'drag-over': isDragging }"
        @dragenter.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @dragover.prevent
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          multiple
          class="hidden-input"
          @change="onFileChange"
        />
        <div class="upload-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="#0ea5e9" d="M12 3a1 1 0 0 1 1 1v8.59l2.3-2.3a1 1 0 1 1 1.4 1.42l-4 4a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.42l2.3 2.3V4a1 1 0 0 1 1-1z"/>
            <path fill="#0ea5e9" d="M4 17a1 1 0 0 1 1-1h14a1 1 0 1 1 0 2H5a1 1 0 0 1-1-1z"/>
          </svg>
        </div>
        <p class="upload-text">Arrastra archivos aquí o haz clic para seleccionar</p>
        <p class="upload-hint">PDF (una o varias páginas), JPG o PNG · Máximo 10 MB por archivo</p>
      </div>

      <!-- ── Clasificar antes de confirmar ────────────────────────────────────── -->
      <div v-if="archivosPendientes.length" class="pendientes-panel">
        <p class="pendientes-title">Clasificar antes de agregar:</p>
        <div
          v-for="(item, idx) in archivosPendientes"
          :key="idx"
          class="pendiente-row"
        >
          <span class="pendiente-nombre">{{ item.file.name }}</span>
          <select v-model="item.tipo" class="tipo-select">
            <option v-for="(label, key) in TIPO_LABELS" :key="key" :value="key">
              {{ label }}
            </option>
          </select>
          <button class="btn-remove-pending" @click="archivosPendientes.splice(idx, 1)"><X :size="18" /></button>
        </div>
        <div class="pendientes-actions">
          <button class="btn-cancel" @click="archivosPendientes = []">Cancelar</button>
          <button class="btn-upload" @click="confirmarArchivos">
            Agregar {{ archivosPendientes.length }} archivo(s)
          </button>
        </div>
      </div>

      <!-- ── Lista: archivos locales (pre-sesión) ──────────────────────────────── -->
      <div v-if="!sesionId && archivosLocales.length" class="doc-list">
        <div v-for="(item, idx) in archivosLocales" :key="idx" class="doc-row">
          <span class="doc-icon">{{ iconFor(item.tipo) }}</span>
          <div class="doc-info">
            <span class="doc-nombre">{{ item.file.name }}</span>
            <span class="doc-tipo">{{ TIPO_LABELS[item.tipo] }}</span>
          </div>
          <button
            class="btn-icon btn-danger"
            title="Quitar"
            @click="quitarLocal(idx)"
          >🗑</button>
        </div>
      </div>

      <!-- ── Lista: documentos del servidor (post-sesión) ─────────────────────── -->
      <div v-if="sesionId && documentosServidor.length" class="doc-list">
        <div v-for="doc in documentosServidor" :key="doc.id" class="doc-row">
          <span class="doc-icon">{{ iconFor(doc.tipo_documento) }}</span>
          <div class="doc-info">
            <span class="doc-nombre">{{ doc.nombre_original }}</span>
            <span class="doc-tipo">{{ TIPO_LABELS[doc.tipo_documento as TipoDocumento] }}</span>
          </div>
          <div class="doc-actions">
            <button class="btn-icon" title="Descargar" @click="descargar(doc)">⬇</button>
            <button
              v-if="puedeEliminar"
              class="btn-icon btn-danger"
              title="Eliminar"
              @click="confirmarEliminar(doc)"
            >🗑</button>
          </div>
        </div>
      </div>

      <p
        v-else-if="!sesionId && !archivosLocales.length && !archivosPendientes.length"
        class="empty-msg"
      >
        No hay archivos seleccionados aún.
      </p>

      <!-- ── Botón extraer ─────────────────────────────────────────────────────── -->
      <div v-if="hayArchivosParaExtraer" class="extraccion-bar">
        <button
          class="btn-extraer"
          :disabled="extrayendo"
          @click="extraer"
        >
          <svg v-if="extrayendo" class="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="#0ea5e9" stroke-width="3" opacity="0.25"/>
            <path d="M22 12a10 10 0 0 1-10 10" stroke="#0ea5e9" stroke-width="3" stroke-linecap="round"/>
          </svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none">
            <circle cx="11" cy="11" r="7" stroke="#0ea5e9" stroke-width="2"/>
            <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round"/>
          </svg>
          {{ extrayendo ? 'Analizando documentos...' : 'Extraer datos del camión' }}
        </button>
        <p class="extraccion-hint">
          Lee automáticamente placa, conductor, guías y más de los documentos adjuntos.
          Los campos del formulario se pre-llenarán para que los revises.
        </p>
      </div>

      <!-- ── Resultado de extracción ───────────────────────────────────────────── -->
      <div v-if="datosExtraidos" class="extraccion-resultado">
        <div class="resultado-header">
          <span class="resultado-titulo">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 20 20" style="vertical-align: middle; margin-right: 0.4em;">
              <circle cx="10" cy="10" r="9" stroke="#22c55e" stroke-width="2" fill="#dcfce7"/>
              <path d="M6 10.5l3 3 5-5" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Formulario pre-llenado
          </span>
          <button class="btn-reextraer" @click="limpiarExtraccion"><X :size="18" /> Limpiar</button>
        </div>

        <div class="campos-grid">
          <div v-for="campo in camposVisibles" :key="campo.key" class="campo-item">
            <label class="campo-label">{{ campo.label }}</label>
            <div class="campo-valor" :class="{ 'no-encontrado': !campo.valor }">
              {{ campo.valor || '—' }}
            </div>
          </div>
        </div>

        <div v-if="datosExtraidos.peso_declarado_tm" class="peso-info">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 20 20" style="vertical-align: middle; margin-right: 0.3em;">
            <g>
              <ellipse cx="10" cy="17" rx="7" ry="1.2" fill="#fde68a"/>
              <rect x="9" y="4" width="2" height="9" rx="1" fill="#f59e42"/>
              <path d="M5 8c0 2.5-2 5-2 5s-2-2.5-2-5a2 2 0 1 1 4 0zm12 0c0 2.5-2 5-2 5s-2-2.5-2-5a2 2 0 1 1 4 0z" fill="#fde68a" stroke="#f59e42" stroke-width="1"/>
              <circle cx="10" cy="4" r="1.2" fill="#f59e42"/>
            </g>
          </svg>
          <span>
            Peso declarado en documentos:
            <strong>{{ datosExtraidos.peso_declarado_tm }} TM</strong>
            <em class="peso-hint"> (referencia — el peso válido es el del ticket de balanza)</em>
          </span>
        </div>

        <p class="resultado-aviso">
          ↑ Revisa los datos en el formulario y corrígelos si es necesario antes de continuar.
        </p>
      </div>
    </section>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted, watch } from 'vue'
  import { useUiStore } from '@/stores/ui'
  import { useAuthStore } from '@/stores/auth'
  import { balanzaApi } from '@/api/balanza'
  import { useSync } from '@/composables/useSync'
  import type { DocumentoRespuesta, DatosExtraidos, TipoDocumento } from '@/types/balanza'

  // ── Props & emits ─────────────────────────────────────────────────────────────
  const props = defineProps<{
    sesionId: number | null
  }>()

  const emit = defineEmits<{
    /**
     * Datos extraídos — pre-llena el formulario del padre inmediatamente.
     * Se emite automáticamente al terminar la extracción.
     */
    (e: 'aplicar', datos: Partial<Record<string, string | null>>): void
    /**
     * Archivos en cola para subir después de crear la sesión (modo pre-sesión).
     * Se emite cada vez que el usuario confirma archivos.
     */
    (e: 'archivos-listos', archivos: Array<{ file: File; tipo: TipoDocumento }>): void
  }>()

  // ── Stores ────────────────────────────────────────────────────────────────────
  const ui   = useUiStore()
  const auth = useAuthStore()

  // ── Estado ────────────────────────────────────────────────────────────────────
  const documentosServidor  = ref<DocumentoRespuesta[]>([])
  const archivosLocales     = ref<Array<{ file: File; tipo: TipoDocumento }>>([])
  const archivosPendientes  = ref<Array<{ file: File; tipo: TipoDocumento }>>([])
  const isDragging          = ref(false)
  const extrayendo          = ref(false)
  const datosExtraidos      = ref<DatosExtraidos | null>(null)
  const fileInput           = ref<HTMLInputElement | null>(null)

  // ── Constantes ────────────────────────────────────────────────────────────────
  const TIPO_LABELS: Record<TipoDocumento, string> = {
    GUIA_REMISION:    'Guía de Remisión (GRR)',
    GUIA_TRANSPORTE:  'Guía de Transporte (GRT)',
    LICENCIA_CONDUCIR: 'Licencia de Conducir',
    OTRO:             'Otro documento',
  }

  // ── Computed ──────────────────────────────────────────────────────────────────
  const puedeEliminar = computed(() =>
    ['Admin', 'Gerencia'].includes(auth.rol ?? '')
  )

  const hayArchivosParaExtraer = computed(() =>
    props.sesionId
      ? documentosServidor.value.length > 0
      : archivosLocales.value.length > 0
  )

  const camposVisibles = computed(() => {
    const d = datosExtraidos.value
    if (!d) return []
    return [
      { key: 'placa',          label: 'Placa',           valor: d.placa },
      { key: 'carreta',        label: 'Carreta',          valor: d.carreta },
      { key: 'conductor',      label: 'Conductor',        valor: d.conductor },
      { key: 'transportista',  label: 'Transportista',    valor: d.transportista },
      { key: 'razon_social',   label: 'Razón Social',     valor: d.razon_social },
      { key: 'ruc_proveedor',  label: 'RUC Proveedor',    valor: d.ruc_proveedor },
      { key: 'guia_remision',  label: 'Guía Remisión',    valor: d.guia_remision },
      { key: 'guia_transporte',label: 'Guía Transporte',  valor: d.guia_transporte },
    ].filter(c => c.valor)   // mostrar solo los que se encontraron
  })

  // ── Lifecycle ─────────────────────────────────────────────────────────────────
  const { online } = useSync()

  onMounted(() => { if (props.sesionId) cargarDelServidor() })
  watch([() => props.sesionId, online], ([id, isOnline]) => {
    if (id && isOnline) cargarDelServidor()
  })

  // ── Métodos: servidor ─────────────────────────────────────────────────────────
  async function cargarDelServidor() {
    if (!props.sesionId) return
    if (!navigator.onLine) return
    try {
      documentosServidor.value = await balanzaApi.listarDocumentos(props.sesionId)
    } catch (err: any) {
      // Si hay error de proxy/red (como ECONNRESET) justo en el milisegundo al reconectar, reintentar.
      if (!err?.response) {
         setTimeout(async () => {
           try { documentosServidor.value = await balanzaApi.listarDocumentos(props.sesionId!) } catch {}
         }, 2000)
      }
    }
  }

  // ── Métodos: selección de archivos ────────────────────────────────────────────
  function onDrop(e: DragEvent) {
    isDragging.value = false
    agregarPendientes(Array.from(e.dataTransfer?.files ?? []))
  }
  function onFileChange(e: Event) {
    const input = e.target as HTMLInputElement
    agregarPendientes(Array.from(input.files ?? []))
    input.value = ''
  }

  function agregarPendientes(files: File[]) {
    const validos = files.filter(f => {
      const ext = f.name.split('.').pop()?.toLowerCase() ?? ''
      if (!['pdf', 'jpg', 'jpeg', 'png'].includes(ext)) {
        ui.toast(`${f.name}: tipo no permitido (PDF, JPG, PNG)`)
        return false
      }
      if (f.size > 10 * 1024 * 1024) {
        ui.toast(`${f.name}: supera 10 MB`)
        return false
      }
      return true
    })

    validos.forEach(file => {
      const n = file.name.toLowerCase()
      let tipo: TipoDocumento = 'OTRO'
      if (n.includes('grr') || n.includes('remision') || n.includes('remitente'))
        tipo = 'GUIA_REMISION'
      else if (n.includes('grt') || n.includes('transporte'))
        tipo = 'GUIA_TRANSPORTE'
      else if (n.includes('licencia') || n.includes('conducir'))
        tipo = 'LICENCIA_CONDUCIR'
      archivosPendientes.value.push({ file, tipo })
    })
  }

  /** Confirma la clasificación y mueve los pendientes a la lista definitiva */
  function confirmarArchivos() {
    if (!archivosPendientes.value.length) return

    if (!props.sesionId) {
      // Pre-sesión: guardar en memoria y notificar al padre
      archivosLocales.value.push(...archivosPendientes.value)
      archivosPendientes.value = []
      datosExtraidos.value = null   // invalidar extracción previa al agregar más
      emit('archivos-listos', [...archivosLocales.value])
    } else {
      // Post-sesión: subir al servidor
      subirAlServidor([...archivosPendientes.value])
      archivosPendientes.value = []
    }
  }

  async function subirAlServidor(items: Array<{ file: File; tipo: TipoDocumento }>) {
    let subidos = 0
    for (const item of items) {
      try {
        const doc = await balanzaApi.subirDocumento(props.sesionId!, item.file, item.tipo)
        documentosServidor.value.push(doc)
        subidos++
      } catch (err: any) {
        ui.toast(`${item.file.name}: ${err?.response?.data?.detail ?? 'Error al subir'}`)
      }
    }
    if (subidos) ui.toast(`${subidos} documento(s) adjuntado(s)`)
    datosExtraidos.value = null
  }

  function quitarLocal(idx: number) {
    archivosLocales.value.splice(idx, 1)
    datosExtraidos.value = null
    emit('archivos-listos', [...archivosLocales.value])
  }

  // ── Métodos: descarga/eliminar servidor ───────────────────────────────────────
  async function descargar(doc: DocumentoRespuesta) {
    try {
      await balanzaApi.descargarDocumento(props.sesionId!, doc.id)
    } catch {
      ui.toast('No se pudo descargar el archivo')
    }
  }

  async function confirmarEliminar(doc: DocumentoRespuesta) {
    const ok = await ui.showConfirm({
      title: 'Eliminar documento',
      message: `¿Eliminar "${doc.nombre_original}"?`,
    })
    if (!ok) return
    try {
      await balanzaApi.eliminarDocumento(props.sesionId!, doc.id)
      documentosServidor.value = documentosServidor.value.filter(d => d.id !== doc.id)
      datosExtraidos.value = null
      ui.toast('Documento eliminado')
    } catch {
      ui.toast('No se pudo eliminar el documento')
    }
  }

  // ── Extracción ────────────────────────────────────────────────────────────────
  async function extraer() {
    extrayendo.value = true
    datosExtraidos.value = null

    try {
      let resultado: DatosExtraidos

      if (props.sesionId) {
        // Modo servidor: el backend lee los archivos guardados
        resultado = await balanzaApi.extraerDatosDocumentos(props.sesionId)
      } else {
        // Modo pre-sesión: enviar TODOS los archivos locales al endpoint stateless
        // (puede ser un PDF con muchas páginas, o múltiples archivos separados)
        if (!archivosLocales.value.length) {
          ui.toast('Agrega al menos un archivo antes de extraer')
          return
        }
        resultado = await balanzaApi.extraerDatosPreview(
          archivosLocales.value.map(a => a.file)   // todos, sin filtrar
        )
      }

      datosExtraidos.value = resultado

      // ── Auto-aplicar al formulario del padre ────────────────────────────────
      // No hace falta un botón "Aplicar" separado — se pre-llena inmediatamente
      // y el usuario lo revisa/edita en el propio formulario.
      const campos: Partial<Record<string, string | null>> = {}
      if (resultado.placa)           campos.placa           = resultado.placa
      if (resultado.carreta)         campos.carreta         = resultado.carreta
      if (resultado.conductor)       campos.conductor       = resultado.conductor
      if (resultado.transportista)   campos.transportista   = resultado.transportista
      if (resultado.razon_social)    campos.razon_social    = resultado.razon_social
      if (resultado.ruc_proveedor)   campos.ruc_proveedor   = resultado.ruc_proveedor
      if (resultado.guia_remision)   campos.guia_remision   = resultado.guia_remision
      if (resultado.guia_transporte) campos.guia_transporte = resultado.guia_transporte
      emit('aplicar', campos)

      const n = Object.keys(campos).length
      ui.toast(`${n} campo(s) pre-llenados — revisa y edita si es necesario`)

    } catch (err: any) {
      ui.toast(err?.response?.data?.detail ?? 'No se pudo extraer datos de los documentos')
    } finally {
      extrayendo.value = false
    }
  }

  function limpiarExtraccion() {
    datosExtraidos.value = null
  }

  // ── Utils ─────────────────────────────────────────────────────────────────────
  function iconFor(tipo: string) {
    const icons: Record<string, string> = {
      GUIA_REMISION: '📄', GUIA_TRANSPORTE: '🚚',
      LICENCIA_CONDUCIR: '🪪', OTRO: '📋',
    }
    return icons[tipo] ?? '📎'
  }
  </script>

  <style scoped>
  .documentos-panel {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .panel-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  .panel-title {
    margin: 0;
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--color-text);
  }
  .doc-count {
    background: var(--color-gold-bg);
    color: var(--color-gold);
    border-radius: 999px;
    padding: 0.1rem 0.6rem;
  font-size: var(--text-sm);
    font-weight: 600;
  }

  /* ── Aviso ───────────────────────────────────────────────────*/
  .aviso-presion {
    display: flex;
    gap: 0.6rem;
    align-items: flex-start;
    background: rgba(14, 165, 233, 0.07);
    border: 1px solid rgba(14, 165, 233, 0.18);
    border-radius: var(--radius-sm);
    padding: 0.65rem 0.85rem;
    font-size: var(--text-md);
    color: var(--color-text-muted);
    line-height: 1.55;
  }
  .aviso-presion p { margin: 0; }

  /* ── Upload zone ─────────────────────────────────────────────*/
  .upload-zone {
    border: 2px dashed var(--color-border);
    border-radius: var(--radius-sm);
    padding: 1.25rem 1rem;
    text-align: center;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
  }
  .upload-zone:hover,
  .upload-zone.drag-over {
    border-color: var(--color-gold);
    background: var(--color-gold-bg);
  }
  .hidden-input { display: none; }
  .upload-icon { font-size: var(--text-xl); margin-bottom: 0.3rem; }
  .upload-text {
    margin: 0 0 0.2rem;
    color: var(--color-text);
    font-size: var(--text-md)rem;
  }
  .upload-hint {
    margin: 0;
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  /* ── Pendientes ──────────────────────────────────────────────*/
  .pendientes-panel {
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: 0.85rem;
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
  }
  .pendientes-title {
    margin: 0;
    font-size: var(--text-md);
    font-weight: 600;
    color: var(--color-text-muted);
  }
  .pendiente-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .pendiente-nombre {
    flex: 1;
    font-size: var(--text-md)rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--color-text);
  }
  .tipo-select {
    flex: 0 0 200px;
    padding: 0.3rem 0.5rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-bg-card);
    color: var(--color-text);
    font-size: var(--text-md);
  }
  .btn-remove-pending {
    background: none;
    border: none;
    color: var(--color-text-muted);
    cursor: pointer;
    font-size: var(--text-md)rem;
    padding: 0.2rem 0.35rem;
    border-radius: 4px;
  }
  .btn-remove-pending:hover { color: #ef4444; background: rgba(239,68,68,.08); }
  .pendientes-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
    padding-top: 0.15rem;
  }
  .btn-cancel {
    padding: 0.38rem 0.9rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: none;
    cursor: pointer;
    font-size: var(--text-md)rem;
    color: var(--color-text-muted);
  }
  .btn-upload {
    padding: 0.38rem 1.1rem;
    border: none;
    border-radius: var(--radius-sm);
    background: var(--color-gold);
    color: #000;
    font-size: var(--text-md)rem;
    font-weight: 600;
    cursor: pointer;
  }

  /* ── Lista de archivos ───────────────────────────────────────*/
  .doc-list {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }
  .doc-row {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.55rem 0.7rem;
    background: var(--color-bg);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border);
  }
  .doc-icon { font-size: var(--text-base); flex-shrink: 0; }
  .doc-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .doc-nombre {
    font-size: var(--text-md)rem;
    font-weight: 500;
    color: var(--color-text);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .doc-tipo { font-size: var(--text-sm); color: var(--color-text-muted); }
  .doc-actions { display: flex; gap: 0.2rem; }
  .btn-icon {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.3rem 0.45rem;
    border-radius: var(--radius-sm);
    font-size: var(--text-md);
    transition: background 0.15s;
  }
  .btn-icon:hover { background: var(--color-gold-bg); }
  .btn-icon.btn-danger:hover { background: rgba(239,68,68,.1); }
  .empty-msg {
    text-align: center;
    color: var(--color-text-muted);
    font-size: var(--text-md)rem;
    margin: 0;
    padding: 0.5rem 0;
  }

  /* ── Botón extraer ───────────────────────────────────────────*/
  .extraccion-bar {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    padding-top: 0.5rem;
    border-top: 1px solid var(--color-border);
  }
  .btn-extraer {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.55rem 1.25rem;
    border: 1px solid var(--color-gold);
    border-radius: var(--radius-sm);
    background: var(--color-gold-bg);
    color: var(--color-gold);
    font-weight: 700;
    font-size: var(--text-base);
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
    align-self: flex-start;
  }
  .btn-extraer:hover:not(:disabled) {
    background: var(--color-gold);
    color: #000;
  }
  .btn-extraer:disabled { opacity: 0.55; cursor: not-allowed; }
  .spinner { animation: spin 1s linear infinite; display: inline-block; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .extraccion-hint {
    margin: 0;
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    line-height: 1.5;
  }

  /* ── Resultado ───────────────────────────────────────────────*/
  .extraccion-resultado {
    background: var(--color-bg);
    border: 1px solid rgba(34, 197, 94, 0.35);
    border-radius: var(--radius-sm);
    padding: 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
  }
  .resultado-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .resultado-titulo {
    font-weight: 700;
    font-size: var(--text-base);
    color: var(--color-text);
  }
  .btn-reextraer {
    padding: 0.25rem 0.6rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: none;
    cursor: pointer;
  font-size: var(--text-sm);
    color: var(--color-text-muted);
  }
  .campos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
    gap: 0.5rem;
  }
  .campo-item { display: flex; flex-direction: column; gap: 0.1rem; }
  .campo-label {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .campo-valor {
    font-size: var(--text-md);
    color: var(--color-text);
    font-weight: 500;
  }
  .campo-valor.no-encontrado { color: var(--color-text-muted); font-style: italic; }
  .peso-info {
    display: flex;
    gap: 0.5rem;
    align-items: flex-start;
    font-size: var(--text-md)rem;
    color: var(--color-text);
    background: var(--color-gold-bg);
    border-radius: var(--radius-sm);
    padding: 0.45rem 0.7rem;
  }
  .peso-hint { color: var(--color-text-muted); font-size: var(--text-sm); }
  .resultado-aviso {
    margin: 0;
  font-size: var(--text-sm);
    color: var(--color-text-muted);
    font-style: italic;
  }
  </style>
