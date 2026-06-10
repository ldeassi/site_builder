let mapsPromise: Promise<void> | null = null

export function getMapsApiKey(): string {
  return (import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '').trim()
}

/**
 * Load Google Maps JS API + Places library for Autocomplete.
 * Uses the callback pattern (required for reliable places library init).
 */
export function ensureGoogleMapsLoaded(): Promise<void> {
  if (typeof window === 'undefined') return Promise.resolve()

  const w = window as any

  if (w.google?.maps?.places?.Autocomplete) {
    return Promise.resolve()
  }

  if (mapsPromise) return mapsPromise

  const apiKey = getMapsApiKey()
  if (!apiKey) {
    return Promise.reject(
      new Error('VITE_GOOGLE_MAPS_API_KEY is not set. Add it to frontend/.env and restart npm run dev'),
    )
  }

  mapsPromise = new Promise<void>((resolve, reject) => {
    const finish = () => {
      if (w.google?.maps?.places?.Autocomplete) {
        console.log('[mapsLoader] Google Maps Places ready')
        resolve()
        return
      }
      // New loader: try importLibrary
      if (w.google?.maps?.importLibrary) {
        w.google.maps.importLibrary('places')
          .then(() => {
            if (w.google?.maps?.places?.Autocomplete) {
              console.log('[mapsLoader] Google Maps Places ready (importLibrary)')
              resolve()
            } else {
              reject(new Error('Places library loaded but Autocomplete is unavailable'))
            }
          })
          .catch(reject)
        return
      }
      reject(new Error('Google Maps loaded but Places library is missing'))
    }

    // Already loading or loaded without places yet
    if (w.google?.maps) {
      finish()
      return
    }

    const existing = document.querySelector(
      'script[src*="maps.googleapis.com/maps/api/js"]',
    ) as HTMLScriptElement | null

    if (existing) {
      existing.addEventListener('load', finish, { once: true })
      existing.addEventListener('error', () => reject(new Error('Google Maps script failed to load')), { once: true })
      if (w.google?.maps) finish()
      return
    }

    console.log('[mapsLoader] Loading Google Maps, key:', `${apiKey.slice(0, 8)}...`)

    w.__siteBuilderMapsInit = () => {
      delete w.__siteBuilderMapsInit
      finish()
    }

    const script = document.createElement('script')
    script.async = true
    script.defer = true
    // Do NOT use loading=async — it breaks legacy google.maps.places.Autocomplete
    script.src =
      `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}` +
      `&libraries=places&callback=__siteBuilderMapsInit`
    script.onerror = () => {
      mapsPromise = null
      reject(new Error(
        'Google Maps failed to load. Check: Maps JavaScript API enabled, billing on, API key allows localhost',
      ))
    }
    document.head.appendChild(script)
  })

  mapsPromise.catch(() => {
    mapsPromise = null
  })

  return mapsPromise
}
