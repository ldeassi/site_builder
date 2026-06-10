import type { DiscoveredBusiness } from '../types/places'

const CSV_HEADERS = [
  'Name',
  'Address',
  'Category',
  'Phone',
  'Email',
  'Rating',
  'Review Count',
  'Google Maps URL',
  'Place ID',
] as const

function escapeCsvCell(value: string | number | null | undefined): string {
  if (value == null) return ''
  const str = String(value)
  if (/[",\n\r]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

export function businessesToCsv(businesses: DiscoveredBusiness[]): string {
  const lines = [CSV_HEADERS.join(',')]
  for (const b of businesses) {
    lines.push(
      [
        b.name,
        b.address,
        b.category,
        b.phone,
        b.email,
        b.rating,
        b.reviewCount,
        b.mapsUrl,
        b.placeId,
      ]
        .map(escapeCsvCell)
        .join(','),
    )
  }
  return lines.join('\r\n')
}

/** Safe filename from location name, e.g. "Leesburg, VA, USA" → "Leesburg_VA_USA" */
export function locationToCsvFilename(locationName: string): string {
  const base = locationName
    .trim()
    .replace(/[^\w\s,-]/g, '')
    .replace(/[\s,]+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '')
  return (base || 'businesses') + '.csv'
}

export function downloadCsvFile(csvContent: string, filename: string): void {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}
