import type { RolSistema } from '@/types/auth'

export interface NavItem {
  label: string
  path:  string
  icon:  string
}

export interface NavSection {
  section: string
  roles:   RolSistema[]   // qué roles ven esta sección
  items:   NavItem[]
}

export interface NavItem {
  label: string
  path:  string
  icon:  string
  roles?: RolSistema[]  // si no viene, hereda los de la sección
}

export const NAV_CONFIG: NavSection[] = [
  {
    section: 'DASHBOARD',
    roles: ['Admin', 'Gerencia', 'Comercial'],
    items: [
      { label: 'Dashboard', path: '/', icon: '▦' },
    ],
  },
  {
    section: 'OPERACIONES',
    roles: ['Admin', 'Gerencia', 'Comercial', 'Operador Balanza', 'Laboratorista', 'Técnico Muestreo'],
    items: [
      { label: 'Balanza',             path: '/balanza',    icon: '⊟', roles: ['Admin', 'Gerencia', 'Comercial', 'Operador Balanza'] },
      { label: 'Muestreo',            path: '/muestreo',   icon: '◈', roles: ['Admin', 'Gerencia', 'Comercial', 'Técnico Muestreo'] },
      { label: 'Pruebas Metalúrgicas',path: '/pruebas',    icon: '⊕', roles: ['Admin', 'Gerencia', 'Comercial', 'Técnico Muestreo'] },
      { label: 'Laboratorio',         path: '/laboratorio',icon: '⊗', roles: ['Admin', 'Gerencia', 'Comercial', 'Laboratorista'] },
      { label: 'Liquidaciones',       path: '/liquidaciones', icon: '≡', roles: ['Admin', 'Gerencia', 'Comercial'] },
      { label: 'Facturación',         path: '/facturacion',icon: '◻', roles: ['Admin', 'Gerencia', 'Comercial'] },
      { label: 'Rumas',               path: '/rumas',      icon: '⬡', roles: ['Admin', 'Gerencia', 'Comercial'] },
    ],
  },
  {
    section: 'GESTIÓN',
    roles: ['Admin', 'Gerencia', 'Comercial'],
    items: [
      { label: 'Terceros',       path: '/terceros',      icon: '◯', roles: ['Admin', 'Gerencia', 'Comercial'] },
      { label: 'Administración', path: '/administracion',icon: '⚙', roles: ['Admin'] },
    ],
  },
]
