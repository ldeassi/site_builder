<template>
  <div class="relative">
    <label for="location-search" class="block text-sm font-medium text-gray-300 mb-2">
      Location
    </label>
    <div class="relative">
      <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </div>
      <input
        id="location-search"
        ref="inputRef"
        v-model="inputValue"
        type="text"
        :placeholder="autocompleteReady
          ? 'Search for a city, town, or area...'
          : 'Enter a city or area name...'"
        class="w-full pl-12 pr-12 py-3.5 rounded-xl bg-gray-900/50 border border-gray-600 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-base transition-all"
        :disabled="disabled"
        autocomplete="off"
      />
      <button
        v-if="inputValue"
        type="button"
        class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-500 hover:text-gray-300 transition-colors"
        @click="clearInput"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div
      v-if="selectedLocation"
      class="mt-3 flex items-center gap-3 bg-cyan-500/10 border border-cyan-500/30 rounded-lg px-4 py-2.5"
    >
      <svg class="w-5 h-5 text-cyan-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M5 13l4 4L19 7" />
      </svg>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-white truncate">{{ selectedLocation.name }}</p>
        <p class="text-xs text-gray-400">Ready to search for businesses without websites</p>
      </div>
      <button
        type="button"
        class="text-gray-500 hover:text-gray-300 transition-colors flex-shrink-0"
        @click="clearSelection"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <p v-if="!selectedLocation && !loadError" class="mt-2 text-xs text-gray-500">
      Pick a city or neighborhood — we'll find local businesses that don't have a website yet.
    </p>
    <p v-if="!selectedLocation && loadError" class="mt-2 text-xs text-red-400/90">
      {{ loadError }}
    </p>
    <p v-else-if="!selectedLocation && !autocompleteReady && !disabled && !hasApiKey" class="mt-2 text-xs text-amber-400/80">
      API key not loaded — add VITE_GOOGLE_MAPS_API_KEY to frontend/.env (no spaces around =) and restart npm run dev
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { ensureGoogleMapsLoaded, getMapsApiKey } from '../services/mapsLoader'
import type { SelectedLocation } from '../types/places'

const props = defineProps<{
  disabled?: boolean
  initialLocation?: SelectedLocation | null
}>()

const emit = defineEmits<{
  (e: 'select', location: SelectedLocation): void
  (e: 'clear'): void
}>()

const inputRef = ref<HTMLInputElement | null>(null)
const inputValue = ref(props.initialLocation?.name || '')
const autocompleteReady = ref(false)
const loadError = ref('')
const selectedLocation = ref<SelectedLocation | null>(props.initialLocation || null)
const hasApiKey = computed(() => !!getMapsApiKey())

watch(() => props.initialLocation, (location) => {
  selectedLocation.value = location || null
  inputValue.value = location?.name || ''
})

let autocompleteInstance: any = null

onMounted(async () => {
  try {
    await ensureGoogleMapsLoaded()
    await nextTick()
    attachAutocomplete()
  } catch (err: any) {
    loadError.value = err?.message || 'Google Maps failed to load'
    console.error('[LocationAutocomplete]', err)
  }
})

function attachAutocomplete() {
  if (!inputRef.value) return
  const google = (window as any).google
  if (!google?.maps?.places?.Autocomplete) {
    loadError.value = 'Places Autocomplete not available after Maps loaded'
    return
  }

  autocompleteInstance = new google.maps.places.Autocomplete(inputRef.value, {
    types: ['(regions)'],
    fields: ['name', 'formatted_address', 'place_id', 'geometry'],
  })

  autocompleteInstance.addListener('place_changed', () => {
    const place = autocompleteInstance?.getPlace()
    if (!place?.geometry?.location || !place.place_id) return

    const name = place.formatted_address || place.name || ''
    const location: SelectedLocation = {
      name,
      placeId: place.place_id,
      lat: place.geometry.location.lat(),
      lng: place.geometry.location.lng(),
    }

    selectedLocation.value = location
    inputValue.value = name
    console.log('[LocationAutocomplete] Location selected:', location)
    emit('select', location)
  })

  autocompleteReady.value = true
}

function clearInput() {
  inputValue.value = ''
  selectedLocation.value = null
  emit('clear')
  inputRef.value?.focus()
}

function clearSelection() {
  clearInput()
}
</script>
