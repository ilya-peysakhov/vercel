<script setup>
import { ref, onMounted, computed, markRaw, nextTick } from 'vue';
import Papa from 'papaparse';
import Plotly from 'plotly.js-dist-min';

// --- State ---
const view = ref('Welcome');
const loading = ref(true);
const error = ref(null);

// We initialize with empty objects to prevent "undefined" errors in the template
const dataStore = ref({
  fighterMap: markRaw(new Map()),
  fighterList: []
});

const f1Selection = ref('Jon Jones');
const f2Selection = ref('Stipe Miocic');

// --- Data Loading ---
const initData = async () => {
  loading.value = true;
  error.value = null;

  Papa.parse("https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fight_stats.csv", {
    download: true,
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    complete: (results) => {
      try {
        const lookup = new Map();
        const names = new Set();

        results.data.forEach(row => {
          if (row.FIGHTER) {
            const name = row.FIGHTER.trim();
            names.add(name);
            if (!lookup.has(name)) lookup.set(name, []);
            lookup.get(name).push(row);
          }
        });

        dataStore.value.fighterMap = markRaw(lookup);
        dataStore.value.fighterList = Array.from(names).sort();
        loading.value = false;
      } catch (e) {
        console.error(e);
        error.value = "Error processing data.";
      }
    },
    error: (err) => {
      error.value = "Failed to download CSV.";
      loading.value = false;
    }
  });
};

// --- Logic (Tale of the Tape) ---
const getStats = (name) => {
  const matches = dataStore.value.fighterMap.get(name) || [];
  let sigLanded = 0;
  matches.forEach(m => {
    const landed = parseInt(String(m['SIG.STR.']).split(' of ')[0]) || 0;
    sigLanded += landed;
  });
  return { sigLanded, count: matches.length };
};

const comparison = computed(() => {
  const s1 = getStats(f1Selection.value);
  const s2 = getStats(f2Selection.value);
  return { s1, s2 };
});

onMounted(initData);
</script>

<template>
  <div class="app">
    <header class="main-header">
      <div class="logo">👊 UFC Explorer</div>
      <nav class="segmented-control">
        <button v-for="t in ['Welcome', 'Fighter One Sheet', 'Tale of the Tape', 'Aggregate Table']" 
                :key="t" :class="{ active: view === t }" @click="view = t">
          {{ t }}
        </button>
      </nav>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Parsing 10,000+ Fight Rows...</p>
    </div>

    <main v-else class="content-area">
      <section v-if="view === 'Welcome'" class="tab-content welcome-tab">
        <h1>UFC Stats v1.0</h1>
        <p>Refactored from Streamlit to Vue 3 for maximum performance.</p>
        <div class="status-chip">Memory: Optimized (0ms lookup)</div>
      </section>

      <section v-if="view === 'Fighter One Sheet'" class="tab-content">
        <div class="controls">
          <select v-model="f1Selection"><option v-for="f in dataStore.fighterList" :value="f">{{ f }}</option></select>
        </div>
        <div class="metric-row">
          <div class="card">Landed: {{ getStats(f1Selection).sigLanded }}</div>
          <div class="card">Fights: {{ getStats(f1Selection).count }}</div>
        </div>
        <div id="stats-plot" class="chart-container"></div>
      </section>

      <section v-if="view === 'Tale of the Tape'" class="tab-content comparison-view">
        <div class="fighter-compare-grid">
          <div class="f-col">
            <select v-model="f1Selection"><option v-for="f in dataStore.fighterList" :value="f">{{ f }}</option></select>
            <div class="adv-badge" v-if="comparison.s1.sigLanded > comparison.s2.sigLanded">ADVANTAGE</div>
          </div>
          <div class="vs-circle">VS</div>
          <div class="f-col">
            <select v-model="f2Selection"><option v-for="f in dataStore.fighterList" :value="f">{{ f }}</option></select>
            <div class="adv-badge" v-if="comparison.s2.sigLanded > comparison.s1.sigLanded">ADVANTAGE</div>
          </div>
        </div>
      </section>

      <section v-if="view === 'Aggregate Table'" class="tab-content">
        <div class="table-wrapper">
          <table>
            <thead>
              <tr><th>Fighter</th><th>Strikes Landed</th><th>Bouts</th></tr>
            </thead>
            <tbody>
              <tr v-for="name in dataStore.fighterList.slice(0, 50)" :key="name">
                <td>{{ name }}</td>
                <td>{{ getStats(name).sigLanded }}</td>
                <td>{{ getStats(name).count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
</template>

<style>
body { margin: 0; background: #0e1117; color: white; font-family: sans-serif; }
.app { padding: 20px; }
nav { display: flex; gap: 10px; margin-bottom: 30px; justify-content: center; }
button { background: #262730; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
button.active { background: #ff4b4b; }
.grid { display: flex; align-items: center; justify-content: center; gap: 40px; }
.vs { font-size: 2rem; font-weight: bold; color: #ff4b4b; }
.stat { margin-top: 20px; font-size: 1.5rem; background: #1e1e1e; padding: 15px; border-radius: 8px; }
select { width: 200px; padding: 10px; background: #262730; color: white; border: 1px solid #444; }
.loading { text-align: center; margin-top: 100px; }
.spinner { border: 4px solid rgba(255,255,255,0.1); border-left-color: #ff4b4b; width: 40px; height: 40px; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
