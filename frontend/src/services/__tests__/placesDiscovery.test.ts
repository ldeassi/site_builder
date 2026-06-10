import { describe, it, expect, vi } from 'vitest'
import { hasWebsite, placeToBusiness, sliceDiscoveryPage, getDiscoveryPageCount, logRawGoogleLegacyApi } from '../placesDiscovery'
import { MAX_DISCOVERY_BUSINESSES } from '../../types/places'

describe('placesDiscovery', () => {
  describe('hasWebsite', () => {
    it('returns false for empty or missing website', () => {
      expect(hasWebsite(undefined)).toBe(false)
      expect(hasWebsite(null)).toBe(false)
      expect(hasWebsite('')).toBe(false)
      expect(hasWebsite('   ')).toBe(false)
    })

    it('returns true when website URI is present', () => {
      expect(hasWebsite('https://example.com')).toBe(true)
    })
  })

  describe('placeToBusiness', () => {
    it('includes hasWebsite true when business has a website', () => {
      const business = placeToBusiness({
        id: 'abc',
        displayName: 'Joe Pizza',
        formattedAddress: '123 Main St',
        websiteURI: 'https://joespizza.com',
      })

      expect(business).toMatchObject({
        placeId: 'abc',
        name: 'Joe Pizza',
        hasWebsite: true,
        websiteUrl: 'https://joespizza.com',
      })
    })

    it('includes hasWebsite false when no website', () => {
      const business = placeToBusiness({
        id: 'abc',
        displayName: 'Local Shop',
        formattedAddress: '456 Oak Ave',
        websiteURI: '',
        rating: 4.5,
        userRatingCount: 12,
        primaryType: 'hair_salon',
      })

      expect(business).toMatchObject({
        placeId: 'abc',
        name: 'Local Shop',
        address: '456 Oak Ave',
        category: 'Hair Salon',
        rating: 4.5,
        reviewCount: 12,
        hasWebsite: false,
        websiteUrl: null,
      })
      expect(business?.mapsUrl).toContain('abc')
    })

    it('returns null when required fields are missing', () => {
      expect(placeToBusiness({ displayName: 'No ID' })).toBeNull()
      expect(placeToBusiness({ id: 'x' })).toBeNull()
    })
  })

  describe('client pagination', () => {
    const sample = (n: number) =>
      Array.from({ length: n }, (_, i) => ({
        placeId: `id-${i}`,
        name: `Biz ${i}`,
        address: '',
        category: 'Business',
        rating: null,
        reviewCount: null,
        mapsUrl: '',
        hasWebsite: false,
        websiteUrl: null,
        phone: null,
        email: null,
      }))

    it('slices 20 items per page', () => {
      const all = sample(45)
      expect(sliceDiscoveryPage(all, 1)).toHaveLength(20)
      expect(sliceDiscoveryPage(all, 2)).toHaveLength(20)
      expect(sliceDiscoveryPage(all, 3)).toHaveLength(5)
    })

    it('caps UI pages at 25 (500 businesses)', () => {
      expect(getDiscoveryPageCount(MAX_DISCOVERY_BUSINESSES)).toBe(25)
      expect(getDiscoveryPageCount(100)).toBe(5)
    })
  })

  describe('logRawGoogleLegacyApi', () => {
    it('logs raw Google API entries to console', () => {
      const groupSpy = vi.spyOn(console, 'group').mockImplementation(() => {})
      const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      logRawGoogleLegacyApi([
        { api: 'legacy_textsearch', results: [{ place_id: 'abc', name: 'Test' }] },
        { api: 'legacy_details', place_id: 'abc', response: { status: 'OK' } },
      ])
      expect(groupSpy).toHaveBeenCalled()
      expect(logSpy).toHaveBeenCalledTimes(2)
      groupSpy.mockRestore()
      logSpy.mockRestore()
    })
  })
})
