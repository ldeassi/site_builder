<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
    <!-- Left: Business discovery -->
    <div class="bg-gray-800/50 rounded-2xl border border-gray-700/50 p-6 space-y-5">
      <div>
        <h3 class="text-lg font-semibold text-white">Find businesses</h3>
        <p class="text-sm text-gray-400 mt-1">
          Search a city or area to discover local businesses and see who has a website.
        </p>
      </div>

      <LocationAutocomplete
        :disabled="store.isSearchingBusinesses"
        :initial-location="store.selectedLocation"
        @select="onLocationSelect"
        @clear="onLocationClear"
      />

      <button
        type="button"
        class="w-full py-3.5 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-2"
        :class="canSearch
          ? 'bg-gray-700 hover:bg-gray-600 text-white border border-gray-600'
          : 'bg-gray-800 text-gray-500 border border-gray-700 cursor-not-allowed'"
        :disabled="!canSearch"
        @click="store.searchBusinessesInLocation()"
      >
        <svg
          v-if="!store.isSearchingBusinesses"
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <svg v-else class="animate-spin h-5 w-5" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        {{ store.isSearchingBusinesses ? 'Searching...' : 'Find businesses' }}
      </button>

      <p v-if="store.businessSearchError" class="text-sm text-red-400">
        {{ store.businessSearchError }}
      </p>
    </div>

    <!-- Right: Site builder -->
    <div class="bg-gray-800/50 rounded-2xl border border-cyan-700/30 p-6 ring-1 ring-cyan-500/10">
      <SiteBuilderPanel />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSiteBuilderStore } from '../stores/siteBuilderStore'
import LocationAutocomplete from './LocationAutocomplete.vue'
import SiteBuilderPanel from './SiteBuilderPanel.vue'
import type { SelectedLocation } from '../types/places'

const store = useSiteBuilderStore()

const canSearch = computed(
  () => !!store.selectedLocation && !store.isSearchingBusinesses,
)

function onLocationSelect(location: SelectedLocation) {
  store.setSelectedLocation(location)
}

function onLocationClear() {
  store.clearSelectedLocation()
}
</script>
