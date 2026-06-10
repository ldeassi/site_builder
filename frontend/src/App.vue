<template>
  <div class="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
    <!-- Header -->
    <header class="border-b border-gray-700/50 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3 cursor-pointer" @click="store.resetToInput()">
          <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold tracking-tight">Site Builder</h1>
            <p class="text-xs text-gray-500 -mt-0.5">URL to Website in 60 seconds</p>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <span
              class="inline-block w-2 h-2 rounded-full animate-pulse"
              :class="store.wsConnected ? 'bg-green-400' : 'bg-red-400'"
            ></span>
            {{ store.wsConnected ? 'Connected' : 'Disconnected' }}
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 w-full" :class="store.phase === 'result' ? '' : 'max-w-7xl mx-auto px-6 py-8'">

      <!-- INPUT PHASE (Dashboard) -->
      <section v-if="store.phase === 'input'" class="space-y-8">
        <div class="text-center mb-4 pt-4">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-medium mb-4">
            <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            Lead discovery & site builder
          </div>
          <h2 class="text-3xl md:text-4xl font-bold text-white mb-2 tracking-tight">
            Find leads.
            <span class="bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent">Build sites.</span>
          </h2>
          <p class="text-gray-400 max-w-2xl mx-auto">
            Search businesses on the left, generate a React website on the right.
          </p>
        </div>

        <Dashboard />
        <SiteHistory />
      </section>

      <!-- DISCOVERY PHASE (results page) -->
      <BusinessDiscoveryPage v-if="store.phase === 'discovery'" />

      <!-- PROGRESS PHASE -->
      <ProgressPanel v-if="store.phase === 'progress'" />

      <!-- RESULT PHASE -->
      <section v-if="store.phase === 'result'">
        <!-- Top bar: title + actions -->
        <div class="flex items-center justify-between px-6 py-3 border-b border-gray-700/50 bg-gray-800/50">
          <div class="flex items-center gap-4">
            <div>
              <h2 class="text-lg font-bold text-white">
                {{ store.resultBusinessName || 'Site Ready' }}
              </h2>
              <p class="text-xs text-gray-400">{{ store.resultTitle }}</p>
            </div>
            <!-- Deploy badge -->
            <a
              v-if="store.resultDeployUrl"
              :href="store.resultDeployUrl"
              target="_blank"
              class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-900/40 border border-emerald-600/30 text-emerald-400 text-xs font-medium hover:bg-emerald-900/60 transition-colors"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              Live
            </a>
          </div>
          <div class="flex items-center gap-2">
            <!-- Toggle editor -->
            <button
              @click="store.editorOpen ? store.closeEditor() : store.openEditor()"
              class="px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2"
              :class="store.editorOpen
                ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/20'
                : 'bg-cyan-600 hover:bg-cyan-500 text-white'"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              {{ store.editorOpen ? 'Hide Editor' : 'Edit Site' }}
            </button>
            <a
              v-if="store.resultDeployUrl"
              :href="store.resultDeployUrl"
              target="_blank"
              class="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition-all"
            >Visit Site</a>
            <a
              :href="store.downloadUrl"
              target="_blank"
              class="px-4 py-2 rounded-lg border border-gray-600 hover:border-gray-400 text-gray-300 hover:text-white text-sm font-semibold transition-all"
            >Download HTML</a>
            <a
              :href="store.downloadSourceUrl"
              target="_blank"
              class="px-4 py-2 rounded-lg border border-cyan-600/50 hover:border-cyan-400 text-cyan-300 hover:text-cyan-200 text-sm font-semibold transition-all"
            >Download source</a>
            <button
              @click="store.resetToInput()"
              class="px-4 py-2 rounded-lg border border-gray-600 hover:border-gray-400 text-gray-300 hover:text-white text-sm font-semibold transition-all"
            >New Site</button>
          </div>
        </div>

        <!-- Editor (left) + Preview (right) layout -->
        <div class="flex">
          <!-- Editor Panel - left side, always visible when open -->
          <EditorPanel v-if="store.editorOpen" />

          <!-- Preview area -->
          <div class="flex-1 min-w-0 p-4">
            <DevicePreview :html="store.resultHtml" />
          </div>
        </div>
      </section>

      <!-- ERROR PHASE -->
      <section v-if="store.phase === 'error'" class="space-y-6">
        <div class="bg-red-900/20 border border-red-700/50 rounded-xl p-6">
          <h3 class="text-red-400 font-semibold text-lg mb-2">Generation Failed</h3>
          <p class="text-red-300">{{ store.errorMessage }}</p>
          <pre
            v-if="store.errorDetails"
            class="mt-4 text-xs text-red-300/70 bg-red-900/20 rounded-lg p-4 overflow-x-auto max-h-48 overflow-y-auto"
          >{{ store.errorDetails }}</pre>
        </div>
        <div class="text-center">
          <button
            @click="store.resetToInput()"
            class="px-6 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold transition-all"
          >
            Try Again
          </button>
        </div>
      </section>

    </main>

    <!-- Footer -->
    <footer class="border-t border-gray-800 py-4 text-center text-xs text-gray-600">
      Site Builder &middot; Powered by Claude AI + Gemini &middot; React + TailwindCSS
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useSiteBuilderStore } from './stores/siteBuilderStore'
import DevicePreview from './components/DevicePreview.vue'
import Dashboard from './components/Dashboard.vue'
import BusinessDiscoveryPage from './components/BusinessDiscoveryPage.vue'
import ProgressPanel from './components/ProgressPanel.vue'
import SiteHistory from './components/SiteHistory.vue'
import EditorPanel from './components/editor/EditorPanel.vue'

const store = useSiteBuilderStore()

onMounted(() => {
  store.initWebSocket()
  store.loadSiteHistory()
  store.loadTemplates()
})

onUnmounted(() => {
  store.destroyWebSocket()
})
</script>

<style scoped>
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}
.slide-fade-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
