<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import Papa from 'papaparse';
import Plotly from 'plotly.js-dist-min';

// --- STATE MANAGEMENT ---
const view = ref('Welcome'); // Replaces st.segmented_control
const loading = ref(true);
const rawStats = ref([]);
const rawFighters = ref([]);
const fighterList = ref([]);

// Selection State
const f1Selection = ref('Jon Jones');
const f2Selection = ref('Stipe Miocic');

const DATA_URLS = {
  stats: "https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fight_stats.csv",
  details: "https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fighter_details.csv"
};

// --- DATA LOADING (Replaces @st.cache_data) ---
const initData = async () => {
  loading.value = true;
  
  // Load Stats CSV
  Papa.parse(DATA_URLS.stats, {
    download: true,
    header: true,
    dynamicTyping: true,
    complete: (statsRes) => {
      rawStats.value = statsRes.data.filter(d => d.FIGHTER);
      fighterList.value = [...new Set(rawStats.value.map(d => d.FIGHTER))].sort();
      
      // Load Fighter Details CSV
      Papa.parse(DATA_URLS.details, {
        download: true,
        header: true,
        complete: (detailRes) => {
          rawFighters.value = detailRes.data;
          loading.value = false;
        }
      });
    }
  });
};

// --- LOGIC HELPERS (Replaces DuckDB Queries) ---
const getFighterMetrics = (name) => {
  const fStats = rawStats.value.filter(d => d.FIGHTER === name);
  const oStats = rawStats.value.filter(d => d.BOUT && fStats.some(fs => fs.BOUT === d.BOUT) && d.FIGHTER !== name);

  const sumLanded = (arr, key) => arr.reduce((acc, r) => acc + (parseInt(String(r[key]).split(' of ')[0]) || 0), 0);
  
  const sigStrLanded = sumLanded(fStats, 'SIG.STR.');
  const sigStrAbs = sumLanded(oStats, 'SIG.STR.');
  const kdCount = fStats.reduce((acc, r) => acc + (r.KD || 0), 0);

  return {
    sigStrDiff: (sigStrLanded / (sigStrAbs || 1)).toFixed(1),
    kd: kdCount,
    fights: [...new Set(fStats.map(d => d.BOUT))].length,
    raw: fStats
  };
};

// --- ADVANTAGE CALCULATOR (Tale of the Tape Logic) ---
const advantages = computed(() => {
  const m1 = getFighterMetrics(f1Selection.value);
  const m2 = getFighterMetrics(f2Selection.value);
  
  let f1Adv = 0; let f2Adv = 0;
  
  if (parseFloat(m1.sigStrDiff) > parseFloat(m2.sigStrDiff)) f1Adv++; else f2Adv++;
  if (m1.kd > m2.kd) f1Adv++; else f2Adv++;
  
  return { f1Adv, f2Adv };
});

// --- CHARTING ---
const renderCharts = () => {
  if (view.value !== 'Fighter One Sheet') return;
  const metrics = getFighterMetrics(f1Selection.value);
  
  const trace = {
    x: metrics.raw.map((_, i) => i + 1),
    y: metrics.raw.map(r => parseInt(String(r['SIG.STR.']).split(' of ')[0]) || 0),
    type: 'scatter', fill: 'tozeroy', line: { color: '#42b883' }
  };

  Plotly.newPlot('stats-plot', [trace], { title: 'Career Striking Volume', paper_bgcolor: 'rgba(0,0,0,0)' });
};

// Watchers to trigger re-renders
watch([view, f1Selection], () => nextTick(() => renderCharts()));

onMounted(initData);
</script>

<template>
  <div class="ufc-app">
    <nav class="segmented-control">
      <button v-for="tab in ['Welcome', 'Fighter One Sheet', 'Tale of the Tape']" 
              :key="tab" :class="{ active: view === tab }" @click="view = tab">
        {{ tab }}
      </button>
    </nav>

    <div v-if="loading" class="loading-screen">Parsing UFC History... 👊</div>

    <main v-else class="content">
      <section v-if="view === 'Welcome'" class="welcome">
        <h1>Welcome to UFC Stats Explorer!</h1>
        <p>The fight data goes back to 1994. Select a view above to begin your analysis.</p>
        <img src="https://media.tenor.com/8jkYjD4cnqUAAAAM/just-bleed.gif" alt="Just Bleed">
      </section>

      <section v-if="view === 'Fighter One Sheet'">
        <div class="filter-bar">
          <select v-model="f1Selection"><option v-for="f in fighterList" :value="f">{{ f }}</option></select>
        </div>
        
        <div class="metrics-grid">
          <div class="metric-card">
            <label>Sig. Strike Diff</label>
            <div class="value">{{ getFighterMetrics(f1Selection).sigStrDiff }}</div>
          </div>
          <div class="metric-card">
            <label>Total UFC Fights</label>
            <div class="value">{{ getFighterMetrics(f1Selection).fights }}</div>
          </div>
        </div>
        <div id="stats-plot"></div>
      </section>

      <section v-if="view === 'Tale of the Tape'" class="tot">
        <div class="comparison-grid">
          <div class="fighter-col">
            <select v-model="f1Selection"><option v-for="f in fighterList" :value="f">{{ f }}</option></select>
            <div class="adv-box" v-if="advantages.f1Adv > advantages.f2Adv">ADVANTAGE</div>
          </div>
          <div class="vs">VS</div>
          <div class="fighter-col">
            <select v-model="f2Selection"><option v-for="f in fighterList" :value="f">{{ f }}</option></select>
            <div class="adv-box" v-if="advantages.f2Adv > advantages.f1Adv">ADVANTAGE</div>
          </div>
        </div>
        <p class="summary">
          {{ advantages.f1Adv > advantages.f2Adv ? f1Selection : f2Selection }} 
          has {{ Math.abs(advantages.f1Adv - advantages.f2Adv) }} more advantages to win.
        </p>
      </section>
    </main>
  </div>
</template>

<style scoped>
.ufc-app { font-family: 'Inter', sans-serif; background: #0e1117; color: white; min-height: 100vh; padding: 20px; }
.segmented-control { display: flex; justify-content: center; gap: 10px; margin-bottom: 30px; }
.segmented-control button { background: #262730; border: none; color: white; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
.segmented-control button.active { background: #ff4b4b; }
.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
.metric-card { background: #262730; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; text-align: center; }
.metric-card label { font-size: 0.75rem; color: #888; text-transform: uppercase; }
.metric-card .value { font-size: 2rem; font-weight: bold; }
.comparison-grid { display: flex; align-items: center; justify-content: space-around; margin-top: 50px; }
.vs { font-size: 3rem; font-weight: 900; font-style: italic; color: #ff4b4b; }
.adv-box { margin-top: 10px; background: #42b883; color: black; font-weight: bold; padding: 5px; border-radius: 3px; }
select { width: 100%; background: #262730; color: white; padding: 12px; border: 1px solid #444; border-radius: 5px; }
.summary { text-align: center; margin-top: 40px; font-size: 1.2rem; background: #1e1e1e; padding: 20px; border-radius: 10px; }
</style>
