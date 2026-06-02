import type { RolSistema } from '@/types/auth'
import type { Component } from 'vue'
import { Scale, FlaskConical, Users, LayoutDashboard, Microscope, Boxes, FileText, Beaker, Settings, Receipt, Weight, Flag, BellRing } from 'lucide-vue-next'

export interface NavItem {
  label: string
  path:  string
  icon:  string | Component
}

export interface NavSection {
  section: string
  roles:   RolSistema[]   // qué roles ven esta sección
  items:   NavItem[]
}

export interface NavItem {
  label: string
  path:  string
  icon:  string | Component
  roles?: RolSistema[]  // si no viene, hereda los de la sección
  disabled?: boolean
}

export const NAV_CONFIG: NavSection[] = [
  {
    section: 'DASHBOARD',
    roles: ['Admin', 'Gerencia', 'Comercial'],
    items: [
      { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    ],
  },
  {
    section: 'OPERACIONES',
    roles: ['Admin', 'Gerencia', 'Comercial', 'OperadorBalanza', 'Laboratorista', 'TecnicoMuestreo', 'Metalurgista'],
    items: [
      { label: 'Balanza', path: '/balanza', icon: Weight, roles: ['Admin', 'Gerencia', 'Comercial', 'OperadorBalanza'] },
      { label: 'Muestreo',            path: '/muestreo',   icon: FlaskConical, roles: ['Admin', 'Gerencia', 'Comercial', 'TecnicoMuestreo'] },
      { label: 'Pruebas Metalúrgicas',path: '/pruebas',    icon: Beaker, roles: ['Admin', 'Gerencia', 'Comercial', 'Metalurgista'] },
      { label: 'Laboratorio',         path: '/laboratorio',icon: Microscope, roles: ['Admin', 'Gerencia', 'Comercial', 'Laboratorista'] },
      { label: 'Liquidaciones',       path: '/liquidaciones', icon: FileText, roles: ['Admin', 'Gerencia', 'Comercial'] },
      { label: 'Facturación',         path: '/facturacion',icon: Receipt, roles: ['Admin', 'Gerencia', 'Comercial'] },
      { label: 'Rumas',               path: '/rumas',      icon: Boxes, roles: ['Admin', 'Gerencia', 'Comercial'] },
    ],
  },
  {
    section: 'GESTIÓN',
    roles: ['Admin', 'Gerencia', 'Comercial'],
    items: [
      { label: 'Terceros',                path: '/terceros',               icon: Users,    roles: ['Admin', 'Gerencia', 'Comercial'] },
      { label: 'Campañas',                path: '/administracion/campanas', icon: Flag,     roles: ['Admin', 'Gerencia'] },
      { label: 'Administración',          path: '/administracion',          icon: Settings, roles: ['Admin'] },
      { label: 'Configuración',           path: '/administracion/config',   icon: BellRing, roles: ['Admin'] },
    ],
  },
]
