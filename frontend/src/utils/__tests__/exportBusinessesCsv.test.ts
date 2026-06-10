import { describe, it, expect } from 'vitest'
import { businessesToCsv, locationToCsvFilename } from '../exportBusinessesCsv'
import type { DiscoveredBusiness } from '../../types/places'

const sample: DiscoveredBusiness = {
  placeId: 'ChIJ123',
  name: 'Joe\'s Pizza',
  address: '123 Main St, Leesburg, VA',
  category: 'Restaurant',
  rating: 4.5,
  reviewCount: 10,
  mapsUrl: 'https://maps.google.com/?q=1',
  hasWebsite: false,
  websiteUrl: null,
  phone: '555-0100',
  email: null,
}

describe('exportBusinessesCsv', () => {
  it('builds CSV with header and escaped special characters', () => {
    const csv = businessesToCsv([{ ...sample, name: 'Joe "Best" Pizza, LLC' }])
    expect(csv).toContain('Name,Address,Category')
    expect(csv).toContain('"Joe ""Best"" Pizza, LLC"')
  })

  it('sanitizes location name for filename', () => {
    expect(locationToCsvFilename('Leesburg, VA, USA')).toBe('Leesburg_VA_USA.csv')
  })
})
