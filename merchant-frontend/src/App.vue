<template>
  <div class="app-shell">
    <AppSidebar v-if="showLayout" />
    <div class="app-main" :class="{ 'is-auth': !showLayout }">
      <AppHeader v-if="showLayout" />
      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'

const route = useRoute()
const showLayout = computed(() => !route.meta?.hideLayout)
</script>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.app-main.is-auth {
  background: radial-gradient(circle at top, #e6edff, #f7f9ff 40%, #f4f7ff 100%);
}

.app-main.is-auth .app-content {
  padding: 0;
  overflow: hidden;
}

.app-content {
  padding: 32px;
  flex: 1;
}

@media (max-width: 960px) {
  .app-shell {
    flex-direction: column;
  }

  .app-content {
    padding: 20px;
  }
}
</style>
