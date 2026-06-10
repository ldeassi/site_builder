import { getMapsApiKey } from './mapsLoader'

import { searchPlacesBulk } from './api'

import type { DiscoveredBusiness, SelectedLocation } from '../types/places'

import {

  DISCOVERY_UI_PAGE_SIZE,

  MAX_DISCOVERY_BUSINESSES,

  MAX_DISCOVERY_UI_PAGES,

} from '../types/places'



const LOG = '[placesDiscovery]'



export interface SearchResult {
  businesses: DiscoveredBusiness[]
  debugLines: string[]
  errors: string[]
  provider?: string
}

/** Print raw Google Legacy API JSON to the browser console (first 5 businesses). */
export function logRawGoogleLegacyApi(rawGoogleLogs: unknown[] | undefined): void {
  if (!rawGoogleLogs?.length) return
  console.group(`${LOG} RAW Google Legacy API (first 5 businesses)`)
  for (const entry of rawGoogleLogs) {
    console.log(entry)
  }
  console.groupEnd()
}



function formatCategory(primaryType?: string, types?: string[]): string {

  const raw = primaryType || types?.find(t => t !== 'point_of_interest' && t !== 'establishment') || types?.[0]

  if (!raw) return 'Business'

  return raw.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

}



function buildMapsUrl(placeId: string, name: string): string {

  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(name)}&query_place_id=${placeId}`

}



export function hasWebsite(websiteUri?: string | null): boolean {

  return typeof websiteUri === 'string' && websiteUri.trim().length > 0

}



export function placeToBusiness(place: {

  id?: string

  displayName?: string | { text?: string }

  formattedAddress?: string

  websiteURI?: string

  nationalPhoneNumber?: string

  internationalPhoneNumber?: string

  rating?: number

  userRatingCount?: number

  primaryType?: string

  types?: string[]

}): DiscoveredBusiness | null {

  const placeId = place.id?.startsWith('places/') ? place.id.slice(7) : place.id

  const displayName = place.displayName

  const name = typeof displayName === 'string' ? displayName : displayName?.text || ''

  if (!placeId || !name) return null

  const websiteUrl = place.websiteURI?.trim() || null

  const phone = place.nationalPhoneNumber || place.internationalPhoneNumber || null

  return {

    placeId,

    name,

    address: place.formattedAddress || '',

    category: formatCategory(place.primaryType, place.types),

    rating: place.rating ?? null,

    reviewCount: place.userRatingCount ?? null,

    mapsUrl: buildMapsUrl(placeId, name),

    hasWebsite: hasWebsite(websiteUrl),

    websiteUrl,

    phone,

    email: null,

  }

}



/**

 * Fetch up to 500 businesses via backend bulk search (server-side Google API).

 * UI pagination (20/page, max 25 pages) is client-side over the returned list.

 */

export async function searchBusinessesInArea(

  location: SelectedLocation,

  onProgress?: (message: string) => void,

): Promise<SearchResult> {

  const apiKey = getMapsApiKey()

  if (!apiKey) {

    throw new Error('VITE_GOOGLE_MAPS_API_KEY is not set. Add it to frontend/.env and restart npm run dev')

  }



  onProgress?.('Searching Google Places via backend…')



  try {

    const result = await searchPlacesBulk({

      locationName: location.name,

      lat: location.lat,

      lng: location.lng,

      maxResults: MAX_DISCOVERY_BUSINESSES,

      apiKey,

    })



    for (const line of result.debugLines) {

      console.log(`${LOG} ${line}`)

      if (line.includes('total')) {

        const match = line.match(/total (\d+)/)

        if (match) onProgress?.(`Found ${match[1]} of up to ${MAX_DISCOVERY_BUSINESSES}…`)

      }

    }



    onProgress?.(`Loaded ${result.businesses.length} businesses`)

    logRawGoogleLegacyApi(result.rawGoogleLogs)

    if (!result.rawGoogleLogs?.length) {
      console.warn(
        `${LOG} No raw Google Legacy API logs — restart backend and ensure Places API (legacy) is enabled`,
      )
    }

    return {
      businesses: result.businesses,
      debugLines: result.debugLines,
      errors: result.errors,
      provider: result.provider,
    }

  } catch (err: unknown) {

    const msg = err instanceof Error ? err.message : String(err)

    if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {

      throw new Error(

        'Cannot reach backend at ' +

          (import.meta.env.VITE_API_BASE_URL || 'http://localhost:9405') +

          '. Start it with: cd backend && python -m uv run python main.py',

      )

    }

    throw err

  }

}



export const searchBusinessesWithoutWebsite = searchBusinessesInArea



export function sliceDiscoveryPage(

  all: DiscoveredBusiness[],

  page: number,

): DiscoveredBusiness[] {

  const totalPages = getDiscoveryPageCount(all.length)

  if (totalPages === 0) return []

  const safePage = Math.min(Math.max(1, page), totalPages)

  const start = (safePage - 1) * DISCOVERY_UI_PAGE_SIZE

  return all.slice(start, start + DISCOVERY_UI_PAGE_SIZE)

}



export function getDiscoveryPageCount(total: number): number {

  if (total === 0) return 0

  return Math.min(MAX_DISCOVERY_UI_PAGES, Math.ceil(total / DISCOVERY_UI_PAGE_SIZE))

}


