import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      name: 'home',
      component: () => import('../views/DashboardView.vue'),
      meta: { module: 'dashboard', title: 'Dashboard' }
    },
    {
      path: '/leads',
      name: 'leads',
      component: () => import('../views/LeadsView.vue'),
      meta: { module: 'crm', title: 'CRM & Leads' }
    },
    {
      path: '/bookings',
      name: 'bookings',
      component: () => import('../views/BookingsView.vue'),
      meta: { module: 'bookings', title: 'Bookings' }
    },
    {
      path: '/dues',
      name: 'dues',
      component: () => import('../views/DuesView.vue'),
      meta: { module: 'dues', title: 'Dues & Collections' }
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('../views/ProjectsView.vue'),
      meta: { module: 'projects', title: 'Projects' }
    },
    {
      path: '/hr',
      name: 'hr',
      component: () => import('../views/EmployeesView.vue'),
      meta: { module: 'hr', title: 'HR & Employees' }
    },
    {
      path: '/stock',
      name: 'stock',
      component: () => import('../views/StockView.vue'),
      meta: { module: 'stock', title: 'Stock & Procurement' }
    },
    {
      path: '/finance',
      name: 'finance',
      component: () => import('../views/FinanceView.vue'),
      meta: { module: 'finance', title: 'Finance' }
    },
    {
      path: '/contractors',
      name: 'contractors',
      component: () => import('../views/ContractorsView.vue'),
      meta: { module: 'contractors', title: 'Contractors' }
    },
    {
      path: '/plots',
      name: 'plots',
      component: () => import('../views/PlotsView.vue'),
      meta: { module: 'plots', title: 'Plots' }
    },
    {
      path: '/approvals',
      name: 'approvals',
      component: () => import('../views/ApprovalsView.vue'),
      meta: { module: 'approvals', title: 'Financial Approvals' }
    },
    {
      path: '/tickets',
      name: 'tickets',
      component: () => import('../views/TicketsView.vue'),
      meta: { module: 'tickets', title: 'Ticketing & Issue' }
    },
    {
      path: '/handover',
      name: 'handover',
      component: () => import('../views/HandoverView.vue'),
      meta: { module: 'handover', title: 'Handover & Post-Sales' }
    },
    {
      path: '/work-orders',
      name: 'workorders',
      component: () => import('../views/WorkOrdersView.vue'),
      meta: { module: 'work-orders', title: 'Work Orders' }
    },
    {
      path: '/labor',
      name: 'labor',
      component: () => import('../views/LaborView.vue'),
      meta: { module: 'labor', title: 'Labor & Workforce' }
    },
    {
      path: '/equipment',
      name: 'equipment',
      component: () => import('../views/EquipmentView.vue'),
      meta: { module: 'equipment', title: 'Equipment & Machinery' }
    },
    {
      path: '/variations',
      name: 'variations',
      component: () => import('../views/VariationOrdersView.vue'),
      meta: { module: 'variations', title: 'Variation Orders' }
    },
    {
      path: '/attendance',
      name: 'attendance',
      component: () => import('../views/AttendanceView.vue'),
      meta: { module: 'attendance', title: 'Attendance & Leave' }
    },
    {
      path: '/leave',
      name: 'leave',
      component: () => import('../views/LeaveView.vue'),
      meta: { module: 'leave', title: 'Leave Requests' }
    },
    {
      path: '/party-ledger',
      name: 'partyledger',
      component: () => import('../views/PartyLedgerView.vue'),
      meta: { module: 'party-ledger', title: 'Party Ledger' }
    },
    {
      path: '/boq',
      name: 'boq',
      component: () => import('../views/BoqView.vue'),
      meta: { module: 'boq', title: 'BOQ & Cost Control' }
    },
    {
      path: '/investments',
      name: 'investments',
      component: () => import('../views/InvestmentsView.vue'),
      meta: { module: 'investments', title: 'Investment & Loans' }
    },
    {
      path: '/loans',
      name: 'loans',
      component: () => import('../views/LoansView.vue'),
      meta: { module: 'loans', title: 'Loans' }
    },
    {
      path: '/fixed-assets',
      name: 'fixedassets',
      component: () => import('../views/FixedAssetsView.vue'),
      meta: { module: 'fixed-assets', title: 'Fixed Assets' }
    },
    {
      path: '/receipts',
      name: 'receipts',
      component: () => import('../views/ReceiptsView.vue'),
      meta: { module: 'receipts', title: 'Goods Receipts' }
    },
    {
      path: '/brokers',
      name: 'brokers',
      component: () => import('../views/BrokersView.vue'),
      meta: { module: 'brokers', title: 'Brokers' }
    },
    {
      path: '/complaints',
      name: 'complaints',
      component: () => import('../views/ComplaintsView.vue'),
      meta: { module: 'complaints', title: 'Complaints & Issues' }
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
      meta: { module: 'settings', title: 'System Settings' }
    },
    {
      path: '/properties',
      name: 'properties',
      component: () => import('../views/PropertiesView.vue'),
      meta: { module: 'properties', title: 'Properties & Units' }
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('../views/TasksView.vue'),
      meta: { module: 'tasks', title: 'Tasks' }
    },
    {
      path: '/customers',
      name: 'customers',
      component: () => import('../views/CustomersView.vue'),
      meta: { module: 'customers', title: 'Customers' }
    },
    {
      path: '/transactions',
      name: 'transactions',
      component: () => import('../views/TransactionsView.vue'),
      meta: { module: 'transactions', title: 'Cash Flow' }
    },
    {
      path: '/suppliers',
      name: 'suppliers',
      component: () => import('../views/SuppliersView.vue'),
      meta: { module: 'suppliers', title: 'Suppliers' }
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('../views/AnalyticsView.vue'),
      meta: { module: 'analytics', title: 'Analytics' }
    },
    {
      path: '/proposals',
      name: 'proposals',
      component: () => import('../views/ProposalsView.vue'),
      meta: { module: 'proposals', title: 'Proposals' }
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('../views/ReportsView.vue'),
      meta: { module: 'reports', title: 'BI Reports' }
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('../views/CalendarView.vue'),
      meta: { module: 'calendar', title: 'Calendar' }
    },
    {
      path: '/announcements',
      name: 'announcements',
      component: () => import('../views/AnnouncementsView.vue'),
      meta: { module: 'announcements', title: 'Announcements' }
    },
    {
      path: '/payroll',
      name: 'payroll',
      component: () => import('../views/PayrollView.vue'),
      meta: { module: 'payroll', title: 'Payroll' }
    },
    {
      path: '/jobs',
      name: 'jobs',
      component: () => import('../views/JobOpeningsView.vue'),
      meta: { module: 'jobs', title: 'Job Openings' }
    },
    {
      path: '/audit-trail',
      name: 'audittrail',
      component: () => import('../views/AuditTrailView.vue'),
      meta: { module: 'audit-trail', title: 'Audit Trail' }
    },
    {
      path: '/campaigns',
      name: 'campaigns',
      component: () => import('../views/CampaignsView.vue'),
      meta: { module: 'campaigns', title: 'Campaigns' }
    },
    {
      path: '/applicants',
      name: 'applicants',
      component: () => import('../views/ApplicantsView.vue'),
      meta: { module: 'applicants', title: 'Job Applicants' }
    },
    {
      path: '/knowledge-base',
      name: 'knowledgebase',
      component: () => import('../views/KnowledgeBaseView.vue'),
      meta: { module: 'knowledge-base', title: 'Knowledge Base' }
    },
    {
      path: '/bank-accounts',
      name: 'bankaccounts',
      component: () => import('../views/BankAccountsView.vue'),
      meta: { module: 'bank-accounts', title: 'Bank Accounts' }
    },
    {
      path: '/backups',
      name: 'backups',
      component: () => import('../views/BackupsView.vue'),
      meta: { module: 'backups', title: 'Data Backup' }
    },
    {
      path: '/compliance',
      name: 'compliance',
      component: () => import('../views/ComplianceView.vue'),
      meta: { module: 'compliance', title: 'Compliance' }
    },
    {
      path: '/legal-contracts',
      name: 'legalcontracts',
      component: () => import('../views/LegalContractsView.vue'),
      meta: { module: 'legal-contracts', title: 'Legal Contracts' }
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/UsersView.vue'),
      meta: { module: 'users', title: 'User & Role Mgmt' }
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/ChatView.vue'),
      meta: { module: 'chat', title: 'Team Chat' }
    },
    {
      path: '/audits',
      name: 'audits',
      component: () => import('../views/AuditsView.vue'),
      meta: { module: 'audits', title: 'QC Audits' }
    },
    {
      path: '/maintenance',
      name: 'maintenance',
      component: () => import('../views/MaintenanceView.vue'),
      meta: { module: 'maintenance', title: 'Maintenance Log' }
    },
    {
      path: '/snags',
      name: 'snags',
      component: () => import('../views/SnagsView.vue'),
      meta: { module: 'snags', title: 'Snags & Handover' }
    },
    {
      path: '/after-sales',
      name: 'aftersales',
      component: () => import('../views/AfterSalesView.vue'),
      meta: { module: 'after-sales', title: 'After-Sales Service' }
    },
    {
      path: '/certificates',
      name: 'certificates',
      component: () => import('../views/CertificatesView.vue'),
      meta: { module: 'certificates', title: 'Certificates' }
    },
    {
      path: '/documents',
      name: 'documents',
      component: () => import('../views/DocumentsView.vue'),
      meta: { module: 'documents', title: 'Document Vault' }
    },
    {
      path: '/designs',
      name: 'designs',
      component: () => import('../views/DesignsView.vue'),
      meta: { module: 'designs', title: 'Designs' }
    },
    {
      path: '/tax-entries',
      name: 'taxentries',
      component: () => import('../views/TaxEntriesView.vue'),
      meta: { module: 'tax-entries', title: 'Tax Entries' }
    },
    {
      path: '/entities',
      name: 'entities',
      component: () => import('../views/EntitiesView.vue'),
      meta: { module: 'entities', title: 'Entities' }
    },
    {
      path: '/opening-balances',
      name: 'openingbalances',
      component: () => import('../views/OpeningBalancesView.vue'),
      meta: { module: 'opening-balances', title: 'Opening Balances' }
    },
    {
      path: '/whatsapp',
      name: 'whatsapp',
      component: () => import('../views/WhatsAppView.vue'),
      meta: { module: 'whatsapp', title: 'WhatsApp Engine' }
    },
    {
      path: '/reminders',
      name: 'reminders',
      component: () => import('../views/ReminderLogView.vue'),
      meta: { module: 'reminders', title: 'Reminder Log' }
    },
    {
      path: '/budgets',
      name: 'budgets',
      component: () => import('../views/BudgetsView.vue'),
      meta: { module: 'budgets', title: 'Project Budgets' }
    },
    {
      path: '/timesheets',
      name: 'timesheets',
      component: () => import('../views/TimesheetsView.vue'),
      meta: { module: 'timesheets', title: 'Timesheets' }
    },
    {
      path: '/contractor-payments',
      name: 'contractorpayments',
      component: () => import('../views/ContractorPaymentsView.vue'),
      meta: { module: 'contractor-payments', title: 'Contractor Payments' }
    },
    {
      path: '/qc-checklist',
      name: 'qcchecklist',
      component: () => import('../views/QcChecklistView.vue'),
      meta: { module: 'qc-checklist', title: 'QC Checklist' }
    },
    {
      path: '/sales-agents',
      name: 'salesagents',
      component: () => import('../views/SalesAgentsView.vue'),
      meta: { module: 'sales-agents', title: 'Sales Agents' }
    },
    {
      path: '/investors',
      name: 'investors',
      component: () => import('../views/InvestorsView.vue'),
      meta: { module: 'investors', title: 'Investors' }
    },
    {
      path: '/journals',
      name: 'journals',
      component: () => import('../views/JournalsView.vue'),
      meta: { module: 'journals', title: 'Journal Entries' }
    },
    {
      path: '/support-tickets',
      name: 'supporttickets',
      component: () => import('../views/SupportTicketsView.vue'),
      meta: { module: 'support-tickets', title: 'Support Tickets' }
    },
    {
      path: '/customer-docs',
      name: 'customerdocs',
      component: () => import('../views/CustomerDocsView.vue'),
      meta: { module: 'customer-docs', title: 'Customer Documents' }
    },
    {
      path: '/credit-notes',
      name: 'creditnotes',
      component: () => import('../views/CreditNotesView.vue'),
      meta: { module: 'credit-notes', title: 'Credit Notes' }
    },
    {
      path: '/recon',
      name: 'recon',
      component: () => import('../views/ReconItemsView.vue'),
      meta: { module: 'recon', title: 'Reconciliation' }
    },
    {
      path: '/transfers',
      name: 'transfers',
      component: () => import('../views/TransfersView.vue'),
      meta: { module: 'transfers', title: 'Transfers' }
    },
    {
      path: '/loan-contracts',
      name: 'loancontracts',
      component: () => import('../views/LoanContractsView.vue'),
      meta: { module: 'loan-contracts', title: 'Loan Contracts' }
    },
    {
      path: '/whatsapp-templates',
      name: 'whatsapptemplates',
      component: () => import('../views/WhatsAppTemplatesView.vue'),
      meta: { module: 'whatsapp-templates', title: 'WhatsApp Templates' }
    },
    {
      path: '/task-comments',
      name: 'taskcomments',
      component: () => import('../views/TaskCommentsView.vue'),
      meta: { module: 'task-comments', title: 'Task Comments' }
    },
    {
      path: '/employee-payroll',
      name: 'employeepayroll',
      component: () => import('../views/EmployeePayrollView.vue'),
      meta: { module: 'employee-payroll', title: 'Employee Payroll' }
    },
    {
      path: '/settings-activity',
      name: 'settingsactivity',
      component: () => import('../views/SettingsActivityView.vue'),
      meta: { module: 'settings-activity', title: 'Settings Activity' }
    },
    {
      path: '/system-docs',
      name: 'systemdocs',
      component: () => import('../views/SystemDocsView.vue'),
      meta: { module: 'system-docs', title: 'System Manual' }
    },
    {
      path: '/qc-reports',
      name: 'qcreports',
      component: () => import('../views/QcReportsView.vue'),
      meta: { module: 'qc-reports', title: 'QC Reports' }
    },
    {
      path: '/copilot',
      name: 'copilot',
      component: () => import('../views/AiCopilotView.vue'),
      meta: { module: 'copilot', title: 'AI Copilot' }
    },
    {
      path: '/empty/:module',
      name: 'empty',
      component: () => import('../views/EmptyStateView.vue'),
      meta: { module: 'empty', title: 'Module' }
    },
    {
      path: '/portal',
      name: 'portal',
      component: () => import('../views/CustomerPortalView.vue'),
      meta: { module: 'portal', title: 'Customer Portal' }
    },
    {
      path: '/flats',
      name: 'flats',
      component: () => import('../views/FlatsView.vue'),
      meta: { module: 'flats', title: 'Flats & Units' }
    },
    {
      path: '/heatmap',
      name: 'heatmap',
      component: () => import('../views/PaymentHeatmapView.vue'),
      meta: { module: 'heatmap', title: 'Payment Heatmap' }
    },
    {
      path: '/sales-config',
      name: 'salesconfig',
      component: () => import('../views/SalesConfigView.vue'),
      meta: { module: 'sales-config', title: 'Sales Config' }
    },
    {
      path: '/license',
      name: 'license',
      component: () => import('../views/LicenseView.vue'),
      meta: { module: 'license', title: 'License & SLA' }
    },
    {
      path: '/permissions',
      name: 'permissions',
      component: () => import('../views/PermissionsView.vue'),
      meta: { module: 'permissions', title: 'Permissions' }
    },
    {
      path: '/csv-import',
      name: 'csvimport',
      component: () => import('../views/CsvImportView.vue'),
      meta: { module: 'csv-import', title: 'CSV Import' }
    },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

// Auth guard: everything except /login requires a session.
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (auth.authenticated && to.name === 'login') return { path: '/' }
    return true
  }
  if (!auth.authenticated) return { path: '/login', query: { redirect: to.fullPath } }
  // Role-based module guard
  const moduleId = to.meta.module as string | undefined
  if (moduleId && !auth.canAccess(moduleId)) return { path: '/' }
  return true
})

export default router
