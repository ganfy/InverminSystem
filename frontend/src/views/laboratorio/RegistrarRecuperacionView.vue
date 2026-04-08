<template>
    <div class="page-container">

      <header class="page-header">
        <div>
          <h1 class="page-title">Registro Análisis Recuperación</h1>
          <p class="page-subtitle" style="color:var(--color-gold);font-family:var(--font-mono)">{{ cipActual }}</p>
        </div>
        <div style="display:flex;gap:0.75rem">
          <button class="btn-secondary" @click="router.back()">← Volver</button>
          <button class="btn-primary" @click="guardar" :disabled="guardando || !pruebaInfo">
            <span v-if="guardando" class="spinner" style="margin-right:0.4rem"></span>
            Generar certificado →
          </button>
        </div>
      </header>

      <div v-if="cargandoInfo" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem"></span> Cargando datos de la prueba...
      </div>

      <div v-else-if="!pruebaInfo" class="estado-tabla" style="color:var(--color-error)">
        Este CIP no corresponde a una prueba completada con ley planta disponible.
        Verificar que el lote tenga análisis de ley vigentes y la prueba haya superado las 48h.
      </div>

      <template v-else>

        <!-- DATOS DEL LOTE -->
        <section class="card">
          <h2 class="card-titulo">DATOS DEL LOTE</h2>
          <div class="form-grid">
            <div class="field">
              <label class="field-label">CIP:</label>
              <input class="field-input" :value="cipActual" disabled style="color:var(--color-gold);font-family:var(--font-mono)" />
            </div>
            <div class="field">
              <label class="field-label">IP (Lote):</label>
              <input class="field-input" :value="pruebaInfo.ip" disabled />
            </div>
            <div class="field">
              <label class="field-label">PROVEEDOR:</label>
              <input class="field-input" :value="pruebaInfo.proveedor" disabled />
            </div>
            <div class="field">
              <label class="field-label">FECHA COMPLETADO:</label>
              <input class="field-input" :value="fmt(pruebaInfo.fecha_salida)" disabled />
            </div>
            <div class="field">
              <label class="field-label">MATERIAL:</label>
              <select class="field-select" v-model="material">
                <option value="Au">Au</option>
                <option value="Ag">Ag</option>
              </select>
            </div>
          </div>
        </section>

        <!-- DATOS DEL ENSAYO -->
        <section class="card">
          <h2 class="card-titulo">DATOS DEL ENSAYO</h2>
          <div class="form-grid">
            <div class="field">
              <label class="field-label">N° INFORME:</label>
              <input class="field-input" v-model="nInforme" placeholder="Ej: AREC-549" />
            </div>
            <div class="field">
              <label class="field-label">FECHA ANÁLISIS:</label>
              <input type="date" class="field-input" v-model="fechaAnalisis" />
            </div>
            <div class="field">
              <label class="field-label">DESCRIPCIÓN:</label>
              <input class="field-input" v-model="descripcion" placeholder="Polveado" />
            </div>
            <div class="field">
              <label class="field-label">MÉTODO:</label>
              <select class="field-select" v-model="metodo">
                <option>Newmont</option><option>Paititi</option><option>Quantum</option><option>Otro</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">PUNTO:</label>
              <select class="field-select" v-model="punto">
                <option>Cola</option><option>Cabeza</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">LABORATORIO:</label>
              <input class="field-input" v-model="form.laboratorio" placeholder="Newmont" />
            </div>
            <div class="field">
              <label class="field-label">SOLICITUD:</label>
              <input class="field-input" value="Análisis de Recuperación" disabled />
            </div>
            <div class="field">
              <label class="field-label">TIPO DE ANÁLISIS:</label>
              <input class="field-input" value="Fire Assay - Gravimétrico" disabled />
            </div>
          </div>
        </section>

        <!-- LEYES -->
        <section class="card">
          <h2 class="card-titulo" style="display:flex;justify-content:space-between;align-items:center">
            <span>LEYES DE LA MUESTRA</span>
            <button v-if="reensayos.length < 2" class="btn-secondary" style="font-size:0.75rem;padding:.35rem .85rem" @click="agregarReensayo">
              + Agregar reensayo
            </button>
          </h2>

          <div class="info-ley-cabeza">
            ℹ️ La <strong>ley cabeza</strong> se obtiene del promedio de análisis de ley vigentes del lote.
            Solo ingresar <strong>ley cola</strong> y <strong>ley líquido</strong>.
          </div>

          <div class="ensayos-grid">

            <!-- Principal -->
            <div class="ensayo-col">
              <h3 class="ensayo-titulo">Ensayo principal</h3>
              <div class="field">
                <label class="field-label">LEY CABEZA (ley planta):</label>
                <div class="ley-cabeza-display">
                  <span class="lc-valor">{{ pruebaInfo.ley_cabeza }}</span>
                  <span class="lc-label">oz/TC — calculada por sistema</span>
                </div>
              </div>
              <div class="field">
                <label class="field-label">LEY COLA:</label>
                <input type="number" class="field-input" v-model.number="form.ley_cola" step="0.001" />
              </div>
              <div class="field">
                <label class="field-label">LEY LÍQUIDO:</label>
                <input type="number" class="field-input" v-model.number="form.ley_liquido" step="0.001" />
              </div>
              <div class="recup-row" v-if="recuperacionPrincipal != null">
                <span class="field-label">RECUPERACIÓN:</span>
                <span class="recup-valor">{{ recuperacionPrincipal.toFixed(2) }}%</span>
              </div>
              <p v-if="errCola" class="error-msg" style="font-size:0.8rem">{{ errCola }}</p>
            </div>

            <!-- Reensayos -->
            <div v-for="(r, i) in reensayos" :key="i" class="ensayo-col">
              <h3 class="ensayo-titulo" style="display:flex;justify-content:space-between">
                <span>Reensayo R{{ i + 1 }}</span>
                <button class="btn-cerrar" @click="reensayos.splice(i, 1)">×</button>
              </h3>
              <div class="field">
                <label class="field-label">LEY CABEZA R{{ i + 1 }}:</label>
                <div class="ley-cabeza-display">
                  <span class="lc-valor">{{ pruebaInfo.ley_cabeza }}</span>
                  <span class="lc-label">oz/TC</span>
                </div>
              </div>
              <div class="field">
                <label class="field-label">LEY COLA R{{ i + 1 }}:</label>
                <input type="number" class="field-input" v-model.number="r.cola" step="0.001" @input="calcRecReensayo(i)" />
              </div>
              <div class="field">
                <label class="field-label">LEY LÍQUIDO R{{ i + 1 }}:</label>
                <input type="number" class="field-input" v-model.number="r.liquido" step="0.001" />
              </div>
              <div class="recup-row" v-if="r.recuperacion != null">
                <span class="field-label">RECUPERACIÓN R{{ i + 1 }}:</span>
                <span class="recup-valor">{{ r.recuperacion.toFixed(2) }}%</span>
              </div>
            </div>

          </div>
          <p v-if="errForm" class="error-msg" style="margin-top:.75rem">{{ errForm }}</p>
        </section>

      </template>
    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useLaboratorioStore } from '@/stores/laboratorio'
  import { pruebasApi, type PruebaRecuperacionItem } from '@/api/pruebas'
  import { useUiStore } from '@/stores/ui'

  const router = useRouter()
  const route  = useRoute()
  const store  = useLaboratorioStore()
  const ui     = useUiStore()

  const cipActual    = route.params.cip as string
  const guardando    = ref(false)
  const cargandoInfo = ref(true)
  const errForm      = ref('')
  const errCola      = ref('')
  const pruebaInfo   = ref<PruebaRecuperacionItem | null>(null)

  const nInforme    = ref('')
  const descripcion = ref('Polveado')
  const metodo      = ref('Newmont')
  const punto       = ref('Cola')
  const material    = ref('Au')
  const fechaAnalisis = ref(new Date().toISOString().split('T')[0])

  const form = ref({
    cip:         cipActual,
    laboratorio: 'Newmont',
    ley_cola:    null as number | null,
    ley_liquido: null as number | null,
  })

  interface Reensayo { cola: number|null; liquido: number|null; recuperacion: number|null }
  const reensayos = ref<Reensayo[]>([])

  const recuperacionPrincipal = computed(() => {
    if (!pruebaInfo.value || !form.value.ley_cola) return null
    const cabeza = Number(pruebaInfo.value.ley_cabeza)
    const cola = form.value.ley_cola
    if (cola >= cabeza) { errCola.value = 'La ley cola debe ser menor a la ley cabeza'; return null }
    errCola.value = ''
    return ((cabeza - cola) / cabeza) * 100
  })

  function calcRecReensayo(i: number) {
    const r = reensayos.value[i]
    if (!r) return
    if (!pruebaInfo.value || !r.cola) { r.recuperacion = null; return }
    const cabeza = Number(pruebaInfo.value.ley_cabeza)
    r.recuperacion = r.cola >= cabeza ? null : ((cabeza - r.cola) / cabeza) * 100
  }

  function agregarReensayo() { reensayos.value.push({ cola: null, liquido: null, recuperacion: null }) }

  function fmt(d: string | null | undefined) {
    if (!d) return '-'
    try {
      const utc = (d.includes('+') || d.endsWith('Z')) ? d : d + 'Z'
      return new Date(utc).toLocaleString('es-PE', { timeZone: 'America/Lima', day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })
    } catch { return '-' }
  }

  onMounted(async () => {
    cargandoInfo.value = true
    try {
      const lista = await pruebasApi.paraRecuperacion()
      pruebaInfo.value = lista.find(p => p.cip === cipActual) ?? null
      if (pruebaInfo.value?.tiene_analisis_recuperacion) {
        ui.toast('Este CIP ya tiene un análisis de recuperación vigente', 'warning')
      }
    } catch {
      ui.toast('Error al cargar datos de la prueba', 'error')
    } finally {
      cargandoInfo.value = false
    }
  })

  async function guardar() {
    errForm.value = ''
    if (!pruebaInfo.value)       { errForm.value = 'Sin datos de prueba'; return }
    if (!form.value.laboratorio) { errForm.value = 'Ingrese el laboratorio'; return }
    if (!form.value.ley_cola)    { errForm.value = 'Ingrese la ley cola'; return }
    const cabeza = Number(pruebaInfo.value.ley_cabeza)
    if (form.value.ley_cola >= cabeza) { errForm.value = 'Ley cola debe ser menor a ley cabeza'; return }

    guardando.value = true
    const ok = await store.registrarRecuperacion({
      cip:            cipActual,
      laboratorio:    form.value.laboratorio,
      ley_cabeza:     cabeza,
      ley_cola:       form.value.ley_cola!,
      ley_liquido:    form.value.ley_liquido,
      origen_datos:   'manual',
      fecha_analisis: fechaAnalisis.value,
    })
    guardando.value = false
    if (ok) router.push('/laboratorio')
  }
  </script>

  <style scoped>
  .ensayos-grid { display:flex; gap:1.5rem; flex-wrap:wrap; align-items:flex-start; }
  .ensayo-col { flex:1; min-width:260px; background:rgba(255,255,255,.03); border:1px solid var(--color-border); border-radius:6px; padding:1rem; display:flex; flex-direction:column; gap:.6rem; }
  .ensayo-titulo { font-family:var(--font-mono); font-size:var(--text-sm); color:var(--color-text-muted); letter-spacing:.06em; text-transform:uppercase; margin-bottom:.25rem; }
  .ley-cabeza-display { display:flex; align-items:baseline; gap:.5rem; padding:.5rem .75rem; background:rgba(184,151,75,.08); border:1px solid rgba(184,151,75,.25); border-radius:4px; }
  .lc-valor { font-family:var(--font-mono); font-size:1.2rem; font-weight:700; color:var(--color-gold); }
  .lc-label { font-size:.7rem; color:var(--color-text-faint); font-family:var(--font-mono); }
  .recup-row { display:flex; align-items:center; gap:.75rem; margin-top:.25rem; }
  .recup-valor { font-family:var(--font-mono); color:var(--color-gold); font-size:var(--text-lg); font-weight:600; }
  .info-ley-cabeza { background:rgba(59,130,246,.08); border:1px solid rgba(59,130,246,.2); border-radius:4px; padding:.6rem .9rem; font-size:var(--text-sm); color:var(--color-text-muted); margin-bottom:1rem; }
  </style>
