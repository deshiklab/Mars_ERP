/**
 * Shell data — GROUPS map mirroring the HTML PWA (groups → modules → routes).
 */
export interface ShellModule {
  id: string
  label: string
  path?: string
}

export interface ShellGroup {
  id: string
  label: string
  /** SVG inner markup (stroke="currentColor" stroke-width="1.5" viewBox 24) */
  svg: string
  module: string // ROLE_MODULES key for access checks
  mods: ShellModule[]
}

export const GROUPS: ShellGroup[] = [
  {
    id: 'executive',
    label: 'Executive',
    svg: '<rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/>',
    module: 'dashboard',
    mods: [
      { id: 'dashboard', label: 'Dashboard', path: '/' },
      { id: 'analytics', label: 'Analytics' , path: '/analytics'},
      { id: 'reports', label: 'Reports' , path: '/reports'},
      { id: 'bi_reports', label: 'BI Reports' , path: '/reports'}
    ]
  },
  {
    id: 'sales_crm',
    label: 'Sales & CRM',
    svg: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    module: 'crm',
    mods: [
      { id: 'customers', label: 'Customers' , path: '/customers'},
      { id: 'crm', label: 'CRM & Leads', path: '/leads' },
      { id: 'proposals', label: 'Proposals' , path: '/proposals'},
      { id: 'contacts', label: 'Contact Book' },
      { id: 'brokers', label: 'Brokers', path: '/brokers' },
      { id: 'complaints', label: 'Complaints', path: '/complaints' },
      { id: 'sales_marketing', label: 'Sales & Marketing' , path: '/sales-config'}
    ]
  },
  {
    id: 'land_projects',
    label: 'Projects',
    svg: '<path d="M2 22V2l20 20H2z"/><path d="M22 2v20H2"/>',
    module: 'projects',
    mods: [
      { id: 'land_mgmt', label: 'Project Acquisition' },
      { id: 'properties_units', label: 'Flats & Units' , path: '/properties'},
      { id: 'plots', label: 'Flats & Units' , path: '/flats'},
      { id: 'layout_builder', label: 'Layout & Unit Builder' },
      { id: 'projects', label: 'Projects', path: '/projects' }
    ]
  },
  {
    id: 'bookings_customer',
    label: 'Bookings & Customer',
    svg: '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="10" x2="21" y2="10"/>',
    module: 'bookings',
    mods: [
      { id: 'bookings', label: 'Bookings', path: '/bookings' },
      { id: 'customer_portal', label: 'Customer Portal' , path: '/portal'},
      { id: 'handover', label: 'Handover & Post-Sales' , path: '/handover'},
      { id: 'dues_recovery', label: 'Dues & Recovery', path: '/dues' },
      { id: 'ticketing', label: 'Ticketing & Issue' }
    ]
  },
  {
    id: 'construction',
    label: 'Engineering & Construction',
    svg: '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    module: 'dashboard',
    mods: [
      { id: 'contractors', label: 'Contractors', path: '/contractors' },
      { id: 'variation_orders', label: 'Variation Orders' , path: '/variations'},
      { id: 'equipment', label: 'Equipment' , path: '/equipment'},
      { id: 'labor', label: 'Labor Mgmt' , path: '/labor'},
      { id: 'designs', label: 'Design Mgmt' , path: '/designs'}
    ]
  },
  {
    id: 'finance_admin',
    label: 'Accounts & Finance',
    svg: '<path d="M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    module: 'dues',
    mods: [
      { id: 'finance', label: 'Finance', path: '/finance' },
      { id: 'party_ledger', label: 'Party Ledger' , path: '/party-ledger'},
      { id: 'payment_heatmap', label: 'Payment Heatmap' , path: '/heatmap'},
      { id: 'approvals', label: 'Financial Approvals' , path: '/approvals'},
      { id: 'boq', label: 'BOQ & Cost Control' , path: '/boq'},
      { id: 'investment_loans', label: 'Investment & Loans' },
      { id: 'fixed_assets', label: 'Fixed Assets' , path: '/fixed-assets'}
    ]
  },
  {
    id: 'hr_admin',
    label: 'Admin & Operations',
    svg: '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    module: 'hr',
    mods: [
      { id: 'hr', label: 'HR', path: '/hr' },
      { id: 'documents', label: 'Documents Vault' , path: '/documents'},
      { id: 'knowledge_base', label: 'Knowledge Base' , path: '/knowledge-base'},
      { id: 'stock', label: 'Stock & Procurement', path: '/stock' }
    ]
  },
  {
    id: 'legal_compliance',
    label: 'Legal & Compliance',
    svg: '<path d="M12 3v18"/><path d="M7 21h10"/><path d="M5 7h14"/><path d="M6 7l-3 5a3 3 0 0 0 6 0L6 7z"/><path d="M18 7l-3 5a3 3 0 0 0 6 0l-3-5z"/>',
    module: 'dashboard',
    mods: [
      { id: 'compliance', label: 'Compliance' , path: '/compliance'},
      { id: 'legal_contracts', label: 'Legal Contracts' },
      { id: 'qc', label: 'QC & Inspection' , path: '/audits'}
    ]
  },
  {
    id: 'collaboration',
    label: 'Collaboration',
    svg: '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    module: 'dashboard',
    mods: [
      { id: 'tasks', label: 'Tasks' , path: '/tasks'},
      { id: 'workspace', label: 'Team Workspace' },
      { id: 'calendar', label: 'Calendar' , path: '/calendar'},
      { id: 'announcements', label: 'Announcements' , path: '/announcements'},
      { id: 'notifications_page', label: 'Notifications' },
      { id: 'activity_log', label: 'Activity Log' , path: '/audit-trail'}
    ]
  },
  {
    id: 'system',
    label: 'System',
    svg: '<circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2"/>',
    module: 'dashboard',
    mods: [
      { id: 'permissions', label: 'Permissions' },
      { id: 'settings', label: 'Settings' , path: '/settings'},
      { id: 'license', label: 'License & SLA' },
      { id: 'system_docs', label: 'System Manual' , path: '/system-docs'},
      { id: 'backup_restore', label: 'Backup & Restore' },
      { id: 'csv_import', label: 'CSV Import' }
    ]
  },
  {
    id: 'communication',
    label: 'Communication & AI',
    svg: '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
    module: 'dashboard',
    mods: [
      { id: 'whatsapp', label: 'WhatsApp Engine' , path: '/whatsapp'},
      { id: 'chat', label: 'Internal Chat' , path: '/chat'},
      { id: 'ai_assistant', label: 'AI Copilot' , path: '/copilot'}
    ]
  }
]

export function groupForPath(path: string): ShellGroup | null {
  for (const g of GROUPS) {
    for (const m of g.mods) {
      if (m.path === path) return g
    }
  }
  return GROUPS[0]
}

export function moduleForPath(path: string): ShellModule | null {
  for (const g of GROUPS) {
    for (const m of g.mods) {
      if (m.path === path) return m
    }
  }
  return null
}
