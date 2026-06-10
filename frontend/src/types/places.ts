export interface SelectedLocation {
  name: string
  placeId: string
  lat: number
  lng: number
}

export interface DiscoveredBusiness {
  placeId: string
  name: string
  address: string
  category: string
  rating: number | null
  reviewCount: number | null
  mapsUrl: string
  hasWebsite: boolean
  websiteUrl: string | null
  phone: string | null
  email: string | null
}

/** Businesses shown per UI page */
export const DISCOVERY_UI_PAGE_SIZE = 20

/** Max businesses to fetch from Google (aggregated across queries) */
export const MAX_DISCOVERY_BUSINESSES = 500

/** Max UI pages: 20 × 25 = 500 */
export const MAX_DISCOVERY_UI_PAGES = 25
