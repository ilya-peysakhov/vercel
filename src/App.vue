<script setup>
import { ref, onMounted, computed } from 'vue';
import Papa from 'papaparse';
import Plotly from 'plotly.js-dist-min';

// State
const fighters = ref([]);
const selectedFighter = ref('Jon Jones');
const fightStats = ref([]);
const loading = ref(true);

const DATA_URLS = {
  stats: "https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fight_stats.csv",
  details: "https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fighter_details.csv"
};

// 1. Load and Parse Data
const initData = async () => {
  loading.value = true;
  Papa.parse(DATA_URLS.stats, {
    download: true,
    header: true,
    dynamicTyping: true,
    complete: (results) => {
      fightStats.value = results.data;
      // Extract unique fighter names for the dropdown
      const names = [...new Set(results.data.map(row => row.FIGHTER))].filter(Boolean).sort();
      fighters.value = names;
      loading.value = false;
      renderChart();
    }
  });
};

// 2. Logic: Filter stats for the selected fighter (Refactoring your DuckDB logic)
const currentFighterStats = computed(() => {
  return fightStats.value.filter(row => row.FIGHTER === selectedFighter.value);
});

const totalSigStr = computed(() => {
  return currentFighterStats.value.reduce((acc, row) => {
    // Handling the 'X of Y' string format from your CSV
    const landed = parseInt(String(row['SIG.STR.']).split(' of ')[0]) || 0;
    return acc + landed;
  }, 0);
});

// 3. Visualization: Plotly Chart
const renderChart = () => {
  const data = currentFighterStats.value;
  if (!data.length) return;

  const trace = {
    x: data.map((_, i) => i + 1), // Using fight index as X-axis
    y: data.map(row => parseInt(String(row['SIG.STR.']).split(' of ')[0]) || 0),
    type: 'scatter',
    mode: 'lines+markers',
    fill: 'tozeroy',
    name: 'Sig. Strikes',
    line: { color: '#42b883' }
  };

  const layout = {
    title: `Striking Trend: ${selectedFighter.value}`,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    xaxis: { title: 'Fight Sequence' },
    yaxis: { title: 'Strikes Landed' }
  };

  Plotly.newPlot('plotly-chart', [trace], layout, { responsive: true });
};

onMounted(initData);
</script>

<template>
  <div class="app-container">
    <h1>👊 UFC Stats Explorer (Vue + Plotly)</h1>

    <div v-if="loading" class="loader">Downloading UFC Dataset...</div>

    <div v-else>
      <div class="sidebar">
        <label>Pick a Fighter:</label>
        <select v-model="selectedFighter" @change="renderChart">
          <option v-for="name in fighters" :key="name" :value="name">{{ name }}</option>
        </select>
      </div>

      <div class="metrics">
        <div class="card">
          <label>Total Career Sig. Strikes</label>
          <div class="val">{{ totalSigStr }}</div>
        </div>
      </div>

      <div id="plotly-chart" style="width:100%; height:400px;"></div>
    </div>
  </div>
</template>

<style scoped>
.app-container { font-family: sans-serif; padding: 20px; max-width: 1000px; margin: auto; }
.sidebar { margin-bottom: 20px; }
.metrics { display: flex; gap: 20px; margin-bottom: 20px; }
.card { background: #f8f9fa; border: 1px solid #ddd; padding: 20px; border-radius: 8px; flex: 1; text-align: center; }
.card label { font-size: 0.8rem; color: #666; text-transform: uppercase; }
.card .val { font-size: 2rem; font-weight: bold; color: #42b883; }
.loader { text-align: center; padding: 50px; font-style: italic; }
select { padding: 10px; width: 100%; border-radius: 4px; border: 1px solid #ccc; }
</style>
