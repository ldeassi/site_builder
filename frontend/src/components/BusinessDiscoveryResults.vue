<template>

  <div class="space-y-4">

    <div

      v-if="businesses.length === 0"

      class="rounded-xl border border-gray-700/50 bg-gray-800/30 px-6 py-10 text-center"

    >

      <p class="text-gray-300 font-medium">{{ emptyMessage || 'No businesses found' }}</p>

      <button

        type="button"

        class="mt-4 px-4 py-2 rounded-lg border border-gray-600 hover:border-gray-400 text-gray-300 hover:text-white text-sm font-medium transition-all"

        @click="$emit('change-location')"

      >

        Change location

      </button>

    </div>



    <template v-else>

      <p class="text-xs text-gray-500">{{ resultsLabel }} · 20 per page</p>



      <ul class="space-y-3">

        <li v-for="business in businesses" :key="business.placeId">

          <button

            type="button"

            class="w-full text-left rounded-xl border px-4 py-4 transition-all"

            :class="selectedPlaceId === business.placeId

              ? 'border-cyan-500/50 bg-cyan-500/10 ring-1 ring-cyan-500/30'

              : 'border-gray-700/50 bg-gray-800/30 hover:border-gray-600 hover:bg-gray-800/50'"

            @click="$emit('select', business)"

          >

            <div class="min-w-0 flex-1 space-y-2">

              <div class="flex items-center gap-2 flex-wrap">

                <p class="font-semibold text-white">{{ business.name }}</p>

                <span

                  v-if="business.hasWebsite"

                  class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/15 border border-blue-500/40 text-blue-300"

                >

                  <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>

                  Website exists

                </span>

                <span

                  v-else

                  class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-500/15 border border-red-500/40 text-red-300"

                >

                  <span class="w-1.5 h-1.5 rounded-full bg-red-400"></span>

                  No website

                </span>

              </div>



              <p class="text-sm text-gray-400">{{ business.address }}</p>



              <div v-if="business.websiteUrl" class="flex items-start gap-2 text-xs">

                <span class="text-gray-500 flex-shrink-0 w-14">Website</span>

                <a

                  :href="business.websiteUrl"

                  target="_blank"

                  rel="noopener noreferrer"

                  class="text-blue-400 hover:text-blue-300 hover:underline break-all"

                  @click.stop

                >

                  {{ business.websiteUrl }}

                </a>

              </div>



              <div class="flex items-start gap-2 text-xs">

                <span class="text-gray-500 flex-shrink-0 w-14">Phone</span>

                <a v-if="business.phone" :href="`tel:${business.phone}`" class="text-gray-300 hover:text-white" @click.stop>

                  {{ business.phone }}

                </a>

                <span v-else class="text-gray-600">Not listed</span>

              </div>



              <div class="flex items-start gap-2 text-xs">

                <span class="text-gray-500 flex-shrink-0 w-14">Email</span>

                <span v-if="business.email" class="text-gray-300 break-all">{{ business.email }}</span>

                <span v-else class="text-gray-600">Not listed on Google</span>

              </div>



              <div class="flex flex-wrap items-center gap-2 pt-1">

                <span class="inline-flex px-2 py-0.5 rounded-md bg-gray-700/60 text-xs text-gray-300">

                  {{ business.category }}

                </span>

                <span v-if="business.rating != null" class="text-xs text-amber-400/90">

                  ★ {{ business.rating.toFixed(1) }}

                  <span v-if="business.reviewCount != null" class="text-gray-500">({{ business.reviewCount }})</span>

                </span>

              </div>

            </div>

          </button>

        </li>

      </ul>



      <div class="flex items-center justify-between gap-3 pt-4 border-t border-gray-700/50">

        <button

          type="button"

          class="px-4 py-2 rounded-lg text-sm font-medium transition-all"

          :class="hasPrev

            ? 'bg-gray-700 text-white hover:bg-gray-600'

            : 'bg-gray-800 text-gray-600 cursor-not-allowed'"

          :disabled="!hasPrev"

          @click="$emit('page-change', currentPage - 1)"

        >

          ← Previous

        </button>



        <span class="text-sm text-gray-400">Page {{ currentPage }} of {{ totalPages }}</span>



        <button

          type="button"

          class="px-4 py-2 rounded-lg text-sm font-medium transition-all"

          :class="hasNext

            ? 'bg-gray-700 text-white hover:bg-gray-600'

            : 'bg-gray-800 text-gray-600 cursor-not-allowed'"

          :disabled="!hasNext"

          @click="$emit('page-change', currentPage + 1)"

        >

          Next →

        </button>

      </div>

    </template>

  </div>

</template>



<script setup lang="ts">

import type { DiscoveredBusiness } from '../types/places'



defineProps<{
  businesses: DiscoveredBusiness[]
  currentPage: number
  totalPages: number
  hasNext: boolean
  hasPrev: boolean
  resultsLabel: string
  emptyMessage?: string
  selectedPlaceId?: string | null
}>()



defineEmits<{

  (e: 'select', business: DiscoveredBusiness): void

  (e: 'change-location'): void

  (e: 'page-change', page: number): void

}>()

</script>


