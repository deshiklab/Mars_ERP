/**
 * i18n — EN / বাংলা toggle mirroring the HTML PWA (_t + _BN_DICT).
 */
import { reactive } from 'vue'

export type Lang = 'en' | 'bn'

/** Core UI strings (subset of the HTML PWA _BN_DICT). */
const BN: Record<string, string> = {
  Dashboard: 'ড্যাশবোর্ড',
  Analytics: 'অ্যানালিটিক্স',
  Reports: 'রিপোর্ট',
  'BI Reports': 'বিআই রিপোর্ট',
  Customers: 'গ্রাহক',
  'CRM & Leads': 'CRM ও লিড',
  Proposals: 'প্রস্তাব',
  'Contact Book': 'কন্টাক্ট বুক',
  'Sales & Marketing': 'বিক্রয় ও মার্কেটিং',
  'Project Acquisition': 'প্রকল্প অধিগ্রহণ',
  'Flats & Units': 'ফ্ল্যাট ও ইউনিট',
  'Plots & Blocks': 'প্লট ও ব্লক',
  'Layout & Unit Builder': 'লেআউট ও ইউনিট বিল্ডার',
  Projects: 'প্রকল্পসমূহ',
  Bookings: 'বুকিং',
  'Customer Portal': 'গ্রাহক পোর্টাল',
  'Handover & Post-Sales': 'হ্যান্ডওভার ও বিক্রয়-পরবর্তী',
  'Dues & Recovery': 'বকেয়া ও আদায়',
  'Ticketing & Issue': 'টিকিট ও সমস্যা',
  Contractors: 'ঠিকাদার',
  'Variation Orders': 'পরিবর্তন আদেশ',
  Equipment: 'যন্ত্রপাতি',
  'Labor Mgmt': 'শ্রম ব্যবস্থাপনা',
  'Design Mgmt': 'ডিজাইন ব্যবস্থাপনা',
  Finance: 'ফাইন্যান্স',
  'Party Ledger': 'পার্টি লেজার',
  'Payment Heatmap': 'পেমেন্ট হিটম্যাপ',
  'Financial Approvals': 'আর্থিক অনুমোদন',
  'BOQ & Cost Control': 'BOQ ও খরচ নিয়ন্ত্রণ',
  'Investment & Loans': 'বিনিয়োগ ও ঋণ',
  'Fixed Assets': 'স্থায়ী সম্পদ',
  HR: 'এইচআর',
  'Documents Vault': 'নথি ভান্ডার',
  'Knowledge Base': 'জ্ঞান ভান্ডার',
  'Stock & Procurement': 'স্টক ও ক্রয়',
  Compliance: 'কমপ্লায়েন্স',
  'Legal Contracts': 'আইনি চুক্তি',
  'QC & Inspection': 'কিউসি ও পরিদর্শন',
  Tasks: 'টাস্ক',
  'Team Workspace': 'টিম ওয়ার্কস্পেস',
  Calendar: 'ক্যালেন্ডার',
  Announcements: 'ঘোষণা',
  Notifications: 'নোটিফিকেশন',
  'Activity Log': 'কার্যকলাপ লগ',
  Permissions: 'অনুমতি',
  Settings: 'সেটিংস',
  'License & SLA': 'লাইসেন্স ও SLA',
  'System Manual': 'সিস্টেম ম্যানুয়াল',
  'Backup & Restore': 'ব্যাকআপ ও পুনরুদ্ধার',
  'CSV Import': 'CSV ইমপোর্ট',
  'WhatsApp Engine': 'হোয়াটসঅ্যাপ ইঞ্জিন',
  'Internal Chat': 'অভ্যন্তরীণ চ্যাট',
  'AI Copilot': 'এআই কপাইলট',
  Session: 'সেশন',
  'Print Report': 'প্রিন্ট রিপোর্ট',
  Role: 'ভূমিকা',
  'Server roles': 'সার্ভার ভূমিকা',
  'Session expires in 8h': 'সেশন ৮ ঘণ্টায় শেষ হবে',
  'Active Bookings': 'সক্রিয় বুকিং',
  'Total Leads': 'মোট লিড',
  'New Inquiry': 'নতুন ইনকোয়ারি',
  'Site Visit': 'সাইট ভিজিট',
  Negotiation: 'আলোচনা',
  Booking: 'বুকিং',
  Lost: 'হারানো',
  'Hot Leads': 'গরম লিড',
  Dues: 'বকেয়া',
  Employees: 'কর্মচারী',
  'HR & Employees': 'এইচআর ও কর্মচারী',
  'Sign Out': 'সাইন আউট',
  'User Profile': 'ব্যবহারকারী প্রোফাইল'
}

export const i18n = reactive({
  lang: (localStorage.getItem('rem_lang') as Lang) || 'en',
  setLang(l: Lang) {
    this.lang = l
    localStorage.setItem('rem_lang', l)
    document.documentElement.lang = l
  },
  toggle() {
    this.setLang(this.lang === 'bn' ? 'en' : 'bn')
  }
})

/** Translate a string (falls back to the original). */
export function _t(s: string): string {
  return i18n.lang === 'bn' ? BN[s] ?? s : s
}
