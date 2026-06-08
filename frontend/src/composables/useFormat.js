export function formatAmount(amount, prefix = '¥', precision = 2) {
  if (amount === null || amount === undefined || isNaN(amount)) return prefix + '0'
  const num = Number(amount).toFixed(precision)
  const parts = num.split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return prefix + parts.join('.')
}

export function formatDate(date, fmt = 'YYYY-MM-DD') {
  if (!date) return '-'
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  return fmt
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

export function formatPercent(value, precision = 1) {
  if (value === null || value === undefined || isNaN(value)) return '0%'
  return Number(value).toFixed(precision) + '%'
}

export function formatMonth(dateStr) {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  return parts[1] || ''
}

export function formatDay(dateStr) {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  return parts[2] || ''
}

export function useFormat() {
  return { formatAmount, formatDate, formatPercent, formatMonth, formatDay }
}
