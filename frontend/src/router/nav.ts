import type { Component } from 'vue'
import { Scale, FlaskConical, Users, LayoutDashboard, Microscope, Boxes, FileText, Beaker, Settings, Receipt, Weight, Flag, BellRing, ShieldCheck } from 'lucide-vue-next'

export interface NavItem {
  label: string
  path:  string
  icon:  string | Component
  /** Permiso requerido para ver este ítem. Si no viene, hereda el de la sección. */
  permiso?: { modulo: string; operacion: string }
  disabled?: boolean
}

export interface NavSection {
  section: string
  /** Permiso requerido para que la sección sea visible. */
  permiso: { modulo: string; operacion: string }
  items:   NavItem[]
}

export const NAV_CONFIG: NavSection[] = [
  {
    section: 'DASHBOARD',
    permiso: { modulo: 'DASHBOARD', operacion: 'VIEW' },
    items: [
      { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    ],
  },
  {
    section: 'OPERACIONES',
    permiso: { modulo: 'BALANZA', operacion: 'VIEW' },   // sección visible si puede ver al menos Balanza
    items: [
      { label: 'Balanza',              path: '/balanza',      icon: Weight,      permiso: { modulo: 'BALANZA',      operacion: 'VIEW' } },
      { label: 'Muestreo',             path: '/muestreo',     icon: FlaskConical,permiso: { modulo: 'MUESTREO',     operacion: 'VIEW' } },
      { label: 'Pruebas Metalúrgicas', path: '/pruebas',      icon: Beaker,      permiso: { modulo: 'PRUEBAS_MET',  operacion: 'VIEW' } },
      { label: 'Laboratorio',          path: '/laboratorio',  icon: Microscope,  permiso: { modulo: 'LABORATORIO',  operacion: 'VIEW' } },
      { label: 'Liquidaciones',        path: '/liquidaciones',icon: FileText,    permiso: { modulo: 'LIQUIDACIONES',operacion: 'VIEW' } },
      { label: 'Rumas',                path: '/rumas',        icon: Boxes,       permiso: { modulo: 'RUMAS',        operacion: 'VIEW' } },
    ],
  },
  {
    section: 'GESTIÓN',
    permiso: { modulo: 'TERCEROS', operacion: 'VIEW' },
    items: [
      { label: 'Terceros',      path: '/terceros',               icon: Users,       permiso: { modulo: 'TERCEROS',       operacion: 'VIEW'   } },
      { label: 'Campañas',      path: '/administracion/campanas',icon: Flag,        permiso: { modulo: 'CAMPANAS',       operacion: 'CREATE' } },
      { label: 'Administración',path: '/administracion',         icon: ShieldCheck, permiso: { modulo: 'ADMINISTRACION', operacion: 'VIEW'   } },
    ],
  },
]
