<script setup>
import { ref, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale)

const fighterName = ref('Jon Jones')
const stats = ref(null)
const loading = ref(false)

// Function to call your Python Backend
async function getFighterData() {
  loading.value = true
  try {
    const response = await fetch(`/api/fighter_stats?name=${fighterName.value}`)
    stats.value = await response.json()
  } catch (err) {
    console.error("Failed to fetch stats", err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  getFighterData()
})
</script>

<template>
  <div class="dashboard">
    <header>
      <h1>👊 UFC Stats Explorer</h1>
      <input v-model="fighterName" @keyup.enter="getFighterData" placeholder="Enter Fighter Name" />
      <button @click="getFighterData">Search</button>
    </header>

    <div v-if="loading">Loading Stats...</div>

    <div v-else-if="stats" class="stats-grid">
      <div class="metric-card">
        <label>Total Fights</label>
        <div class="value">{{ stats.total_fights }}</div>
      </div>
      <div class="metric-card">
        <label>Sig. Strikes Landed</label>
        <div class="value">{{ stats.sig_str_landed }}</div>
      </div>
      <div class="metric-card">
        <label>Knockdowns</label>
        <div class="value">{{ stats.knockdowns }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard { padding: 2rem; font-family: sans-serif; background: #f4f4f9; min-height: 100vh; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 2rem; }
.metric-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
.metric-card label { color: #666; font-size: 0.9rem; }
.metric-card .value { font-size: 2rem; font-weight: bold; color: #42b883; }
input { padding: 8px; border-radius: 4px; border: 1px solid #ccc; margin-right: 10px; }
</style>
