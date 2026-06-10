<template>
  <div class="space-y-5">
    <div>
      <h3 class="text-lg font-semibold text-white">Generate a website</h3>
      <p class="text-sm text-gray-400 mt-1">
        Search for a business on Google Maps, pick a template, and build a React site in about a minute.
      </p>
    </div>

    <PlacesAutocomplete
      :disabled="store.isGenerating"
      :model-value="store.inputUrl"
      :bias-lat="store.selectedLocation?.lat"
      :bias-lng="store.selectedLocation?.lng"
      @select="onPlaceSelect"
      @website-url="onWebsiteUrl"
      @clear="onClear"
    />

    <TemplateCards
      :selected="store.templateName"
      @select="name => (store.templateName = name)"
    />

    <button
      type="button"
      class="w-full py-4 rounded-xl font-bold text-lg transition-all duration-200 flex items-center justify-center gap-3"
      :class="store.canGenerate && !store.isGenerating
        ? 'bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white shadow-lg shadow-cyan-600/20 hover:shadow-cyan-500/30 cursor-pointer hover:scale-[1.01] active:scale-[0.99]'
        : 'bg-gray-700 text-gray-400 cursor-not-allowed'"
      :disabled="!store.canGenerate || store.isGenerating"
      @click="store.startGeneration()"
    >
      <svg
        v-if="!store.isGenerating"
        class="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
      <svg v-else class="animate-spin h-5 w-5" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
      {{ store.isGenerating ? 'Starting...' : 'Generate Site' }}
    </button>

    <p v-if="!store.canGenerate" class="text-xs text-gray-500 text-center">
      Select a business from the dropdown or paste a Google Maps / website URL
    </p>
  </div>
</template>

<script setup lang="ts">
import { useSiteBuilderStore } from '../stores/siteBuilderStore'
import PlacesAutocomplete from './PlacesAutocomplete.vue'
import TemplateCards from './TemplateCards.vue'

const store = useSiteBuilderStore()

interface SelectedPlace {
  name: string
  address: string
  placeId: string | null
  mapsUrl: string
}

function onPlaceSelect(place: SelectedPlace) {
  store.setInputUrl(place.mapsUrl)
  store.businessNameInput = place.name
  if (place.address && !store.businessCategoryInput) {
    store.businessCategoryInput = ''
  }
}

function onWebsiteUrl(url: string) {
  store.setInputUrl(url)
  store.businessNameInput = store.businessNameInput || ''
}

function onClear() {
  store.mapsUrl = ''
  store.websiteUrl = ''
  store.inputUrl = ''
  store.inputUrlType = 'none'
  store.businessNameInput = ''
}
</script>
