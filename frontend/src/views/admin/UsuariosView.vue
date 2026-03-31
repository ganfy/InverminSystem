<template>
  <div class="usuarios-page">
    <div class="page-header">
      <h1 class="page-title">Gestión de Usuarios</h1>
      <button class="btn-primary" @click="abrirCrear">+ Nuevo usuario</button>
    </div>

    <!-- Filtros -->
    <div class="filtros">
      <select class="field-input filtro-select" v-model="filtroRol">
        <option value="">Todos los roles</option>
        <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
      </select>
      <select class="field-input filtro-select" v-model="filtroEstado">
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

    <!-- Tabla -->
    <div class="tabla-wrapper">
      <div v-if="loading" class="estado-tabla">Cargando...</div>
      <div v-else-if="error" class="estado-tabla error-msg">{{ error }}</div>
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
            <td><span class="badge-rol" :class="rolClass(u.rol)">{{ u.rol }}</span></td>
            <td>
              <span class="badge-estado" :class="u.activo ? 'activo' : 'inactivo'">
                {{ u.activo ? 'ACTIVO' : 'INACTIVO' }}
              </span>
            </td>
            <td class="td-fecha">{{ formatFecha(u.creado_en) }}</td>
            <td class="td-acciones">
              <button class="btn-icon" title="Editar" @click="abrirEditar(u)">✎</button>
              <button
                class="btn-icon"
                :title="u.activo ? 'Desactivar' : 'Activar'"
                @click="toggleEstado(u)"
              >{{ u.activo ? '⊘' : '⊕' }}</button>
              <button class="btn-icon" title="Reset password" @click="abrirReset(u)">🔑</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal crear/editar -->
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
              <select class="field-input" v-model="form.rol">
                <option value="" disabled>Seleccionar rol</option>
                <option v-for="r in ROLES" :key="r" :value="r">{{ r }}</option>
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
          <button class="btn-primary" :disabled="guardando" @click="guardar">
            {{ guardando ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal reset password -->
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
          <button class="btn-primary" :disabled="guardando" @click="confirmarReset">
            {{ guardando ? 'Guardando...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usuariosApi, type UsuarioListItem } from '@/api/usuarios'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()

const ROLES = [
  'Admin',
  'Gerencia',
  'Comercial',
  'Laboratorista',
  'Operador Balanza',
  'Técnico Muestreo',
]

// Estado principal
const usuarios   = ref<UsuarioListItem[]>([])
const loading    = ref(false)
const error      = ref('')

// Filtros
const filtroRol    = ref('')
const filtroEstado = ref('')
const busqueda     = ref('')

// Modal crear/editar
const modalVisible = ref(false)
const modoEditar   = ref(false)
const guardando    = ref(false)
const formError    = ref('')
const editandoId   = ref<number | null>(null)

const form = ref({
  nombre_completo: '',
  username: '',
  rol: '',
  email: '',
  password: '',
})

// Modal reset
const resetVisible  = ref(false)
const usuarioReset  = ref<UsuarioListItem | null>(null)
const nuevaPassword = ref('')
const resetError    = ref('')

// ── Computed ──────────────────────────────────────────────
const usuariosFiltrados = computed(() => {
  return usuarios.value.filter(u => {
    if (filtroRol.value && u.rol !== filtroRol.value) return false
    if (filtroEstado.value === 'activo' && !u.activo) return false
    if (filtroEstado.value === 'inactivo' && u.activo) return false
    if (busqueda.value) {
      const q = busqueda.value.toLowerCase()
      return u.nombre_completo.toLowerCase().includes(q) ||
             u.username.toLowerCase().includes(q)
    }
    return true
  })
})

// ── Helpers ───────────────────────────────────────────────
function formatFecha(iso: string) {
  const utc = (iso.includes('+') || iso.endsWith('Z')) ? iso : iso + 'Z'
  return new Date(utc).toLocaleString('es-PE', {
    timeZone: 'America/Lima',
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function rolClass(rol: string) {
  const map: Record<string, string> = {
    'Admin':            'rol-admin',
    'Gerencia':         'rol-gerencia',
    'Comercial':        'rol-comercial',
    'Laboratorista':    'rol-lab',
    'Operador Balanza': 'rol-operador',
    'Técnico Muestreo': 'rol-tecnico',
  }
  return map[rol] ?? ''
}

// ── Carga ─────────────────────────────────────────────────
async function cargar() {
  loading.value = true
  error.value = ''
  try {
    usuarios.value = await usuariosApi.listar()
  } catch {
    error.value = 'Error al cargar usuarios'
  } finally {
    loading.value = false
  }
}

// ── Modal crear/editar ────────────────────────────────────
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

function cerrarModal() {
  modalVisible.value = false
}

async function guardar() {
  formError.value = ''
  if (!form.value.nombre_completo || !form.value.rol) {
    formError.value = 'Nombre y rol son obligatorios'
    return
  }
  if (!modoEditar.value && (!form.value.username || !form.value.password)) {
    formError.value = 'Usuario y contraseña son obligatorios'
    return
  }

  guardando.value = true
  try {
    if (modoEditar.value && editandoId.value) {
      await usuariosApi.editar(editandoId.value, {
        nombre_completo: form.value.nombre_completo,
        rol: form.value.rol,
        email: form.value.email || undefined,
      })
    } else {
      await usuariosApi.crear({
        username:        form.value.username,
        password:        form.value.password,
        nombre_completo: form.value.nombre_completo,
        rol:             form.value.rol,
        email:           form.value.email || undefined,
      })
    }
    cerrarModal()
    await cargar()
    ui.toast(modoEditar.value ? 'Usuario actualizado' : 'Usuario creado', 'success')
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al guardar', 'error')
  } finally {
    guardando.value = false
  }
}

// ── Toggle estado ─────────────────────────────────────────
async function toggleEstado(u: UsuarioListItem) {
  const ok = await ui.showConfirm({
    title:         u.activo ? 'Desactivar usuario' : 'Activar usuario',
    message:       u.activo
      ? `¿Desactivar a ${u.nombre_completo}? No podrá ingresar al sistema.`
      : `¿Reactivar acceso de ${u.nombre_completo}?`,
    confirmLabel:  u.activo ? 'Desactivar' : 'Activar',
    danger:        u.activo,
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
    await cargar()
  } catch {
    ui.toast('Error al cambiar estado', 'error')
  }
}

// ── Reset password ────────────────────────────────────────
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
  guardando.value = true
  try {
    await usuariosApi.resetPassword(usuarioReset.value!.id, nuevaPassword.value)
    resetVisible.value = false
    ui.toast('Contraseña actualizada', 'success')
  } catch {
    resetError.value = 'Error al cambiar contraseña'
    ui.toast('Error al cambiar contraseña', 'error')
  } finally {
    guardando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>

.filtros {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}
.filtro-select { width: 180px; }
.filtro-search { flex: 1; min-width: 200px; }

.field-input.disabled { opacity: 0.5; cursor: not-allowed; }

.reset-usuario {
  color: var(--color-text-muted);
  margin-bottom: 1rem;
  font-size: var(--text-base);
}
.reset-usuario strong { color: var(--color-text); }
</style>
