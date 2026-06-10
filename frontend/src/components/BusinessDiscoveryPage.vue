<template>
  <section class="space-y-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <button
          type="button"
          class="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition-colors mb-3"
          @click="store.goBackToDashboard()"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to search
        </button>
        <h2 class="text-3xl font-bold text-white tracking-tight">
          Businesses in {{ store.selectedLocation?.name }}
        </h2>
        <p v-if="!store.isSearchingBusinesses && store.discoveryAllBusinesses.length" class="text-gray-400 mt-1">
          {{ store.discoveryResultsLabel }} ·
          <span class="text-red-400">{{ noWebsiteCount }} no website</span> ·
          <span class="text-blue-400">{{ withWebsiteCount }} with website</span>
        </p>
      </div>

      <div v-if="!store.isSearchingBusinesses" class="flex flex-col gap-2 text-xs flex-shrink-0">
        <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-300">
          <span class="w-2 h-2 rounded-full bg-blue-400"></span>
          Website exists
        </span>
        <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300">
          <span class="w-2 h-2 rounded-full bg-red-400"></span>
          No website
        </span>
      </div>
    </div>

    <div
      v-if="store.isSearchingBusinesses"
      class="rounded-2xl border border-gray-700/50 bg-gray-800/50 py-24 text-center"
    >
      <svg class="animate-spin h-12 w-12 text-cyan-400 mx-auto mb-4" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
      <p class="text-gray-200 font-medium text-lg">Searching Google Places…</p>
      <p class="text-sm text-gray-500 mt-1">Loading up to 500 businesses — this may take 1–2 minutes</p>
      <p v-if="store.discoverySearchProgress" class="text-sm text-cyan-400/80 mt-3">{{ store.discoverySearchProgress }}</p>
    </div>

    <div v-else class="rounded-2xl border border-gray-700/50 bg-gray-800/50 p-6">
      <div
        v-if="store.discoveryAllBusinesses.length"
        class="flex flex-wrap items-center justify-between gap-3 mb-4 pb-4 border-b border-gray-700/50"
      >
        <p class="text-sm text-gray-400">Filter & export</p>
        <div class="flex flex-wrap items-center gap-2">
          <button
            type="button"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all border"
            :class="store.discoveryNoWebsiteOnly
              ? 'bg-red-500/15 border-red-500/40 text-red-300'
              : 'bg-gray-800 border-gray-600 text-gray-300 hover:border-gray-500 hover:text-white'"
            @click="store.setDiscoveryNoWebsiteOnly(!store.discoveryNoWebsiteOnly)"
          >
            <span
              class="w-2 h-2 rounded-full"
              :class="store.discoveryNoWebsiteOnly ? 'bg-red-400' : 'bg-gray-500'"
            />
            No website only
          </button>
          <button
            type="button"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all border bg-gray-800 border-gray-600 text-gray-300 hover:border-cyan-500/50 hover:text-cyan-300 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-gray-600 disabled:hover:text-gray-300"
            :disabled="noWebsiteCount === 0"
            :title="noWebsiteCount === 0 ? 'No businesses without a website' : `Export ${noWebsiteCount} businesses as CSV`"
            @click="store.exportNoWebsiteBusinessesCsv()"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4" />
            </svg>
            Export no-website CSV
          </button>
        </div>
      </div>

      <BusinessDiscoveryResults
        v-if="store.selectedLocation"
        :businesses="store.discoveredBusinesses"
        :current-page="store.discoveryPage"
        :total-pages="store.discoveryTotalPages"
        :has-next="store.hasNextDiscoveryPage"
        :has-prev="store.hasPrevDiscoveryPage"
        :results-label="store.discoveryResultsLabel"
        :empty-message="store.discoveryNoWebsiteOnly
          ? 'No businesses without a website'
          : 'No businesses found'"
        :selected-place-id="store.selectedDiscoveredBusiness?.placeId"
        @select="store.selectDiscoveredBusiness"
        @change-location="store.goBackToDashboard()"
        @page-change="store.setDiscoveryPage"
      />

      <div
        v-if="store.selectedDiscoveredBusiness"
        class="mt-6 pt-6 border-t border-gray-700/50 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4"
      >
        <div class="min-w-0">
          <p class="text-sm text-gray-400">Selected for site generation</p>
          <p class="font-semibold text-white truncate">{{ store.selectedDiscoveredBusiness.name }}</p>
        </div>
        <button
          type="button"
          class="px-6 py-3 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 shrink-0"
          :class="store.canGenerate && !store.isGenerating
            ? 'bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white shadow-lg shadow-cyan-600/20'
            : 'bg-gray-700 text-gray-400 cursor-not-allowed'"
          :disabled="!store.canGenerate || store.isGenerating"
          @click="store.startGeneration()"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Generate Site
        </button>
      </div>

      <p v-if="store.businessSearchError" class="text-sm text-red-400 mt-4 text-center">
        {{ store.businessSearchError }}
      </p>

      <details v-if="store.businessSearchDebug.length" class="mt-4 rounded-lg border border-gray-700/50 bg-gray-900/50">
        <summary class="px-4 py-2 text-xs text-gray-400 cursor-pointer hover:text-gray-300">
          Search log ({{ store.businessSearchDebug.length }} lines)
        </summary>
        <pre class="px-4 py-3 text-xs text-gray-500 overflow-x-auto max-h-48 overflow-y-auto whitespace-pre-wrap">{{ store.businessSearchDebug.join('\n') }}</pre>
      </details>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSiteBuilderStore } from '../stores/siteBuilderStore'
import BusinessDiscoveryResults from './BusinessDiscoveryResults.vue'

const store = useSiteBuilderStore()

const noWebsiteCount = computed(
  () => store.discoveryAllBusinesses.filter(b => !b.hasWebsite).length,
)
const withWebsiteCount = computed(
  () => store.discoveryAllBusinesses.filter(b => b.hasWebsite).length,
)
</script>
