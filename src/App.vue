<script setup>
import { ref, onMounted, computed, markRaw, watch, nextTick } from 'vue';
import Papa from 'papaparse';
import Plotly from 'plotly.js-dist-min';

// --- APPLICATION STATE ---
const view = ref('Welcome');
const loading = ref(true);
const f1Selection = ref('Jon Jones');
const f2Selection = ref('Stipe Miocic');

const dataStore = ref({
  fighterMap: markRaw(new Map()),
  fighterList: []
});

const DATA_URL = "https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fight_stats.csv";

// --- DATA INITIALIZATION (The "DuckDB" replacement) ---
const initData = async () => {
  loading.value = true;
  Papa.parse(DATA_URL, {
    download: true,
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    complete: (results) => {
      const lookup = new Map();
      const names = new Set();

      // We process the CSV once and build a Map of Stats for every fighter
      results.data.forEach(row => {
        if (!row.FIGHTER || !row.BOUT) return;
        const name = row.FIGHTER.trim();
        names.add(name);
        
        if (!lookup.has(name)) lookup.set(name, []);
        lookup.get(name).push(row);
      });

      dataStore.value.fighterMap = markRaw(lookup);
      dataStore.value.fighterList = Array.from(names).sort();
      loading.value = false;
    }
  });
};

// --- CORE LOGIC (Refactored from your Python calculations) ---
const getFighterMetrics = (name) => {
  const fStats = dataStore.value.fighterMap.get(name) || [];
  if (!fStats.length) return { sigStr: 0, headMovement: 0, tdLanded: 0, fights: 0 };

  let totalHeadAtt = 0;
  let totalHeadLanded = 0;
  let totalTdLanded = 0;
  let totalSigLanded = 0;

  fStats.forEach(s => {
    // Parse "X of Y" strings
    const [hL, hA] = String(s['HEAD'] || "0 of 0").split(' of ').map(v => parseInt(v) || 0);
    const [tdL, tdA] = String(s['TD'] || "0 of 0").split(' of ').map(v => parseInt(v) || 0);
    const [sigL, sigA] = String(s['SIG.STR.'] || "0 of 0").split(' of ').map(v => parseInt(v) || 0);

    totalHeadLanded += hL;
    totalHeadAtt += hA;
    totalTdLanded += tdL;
    totalSigLanded += sigL;
  });

  // Head Movement Calculation from your Python: landed / attempted
  const headMovePercent = totalHeadAtt > 0 ? (totalHeadLanded / totalHeadAtt) * 100 : 0;

  return {
    sigStr: totalSigLanded,
    headMovement: headMovePercent.toFixed(1),
    tdLanded: totalTdLanded,
    fights: fStats.length,
    raw: fStats
  };
};

// --- ADVANTAGE CALCULATOR (Tale of the Tape) ---
const comparison = computed(() => {
  const f1 = getFighterMetrics(f1Selection.value);
  const f2 = getFighterMetrics(f2Selection.value);
  
  let f1Adv = 0;
  let f2Adv = 0;

  if (parseFloat(f1.headMovement) > parseFloat(f2.headMovement)) f1Adv++; else f2Adv++;
  if (f1.tdLanded > f2.tdLanded) f1Adv++; else f2Adv++;
  if (f1.sigStr > f2.sigStr) f1Adv++; else f2Adv++;

  return { f1, f2, f1Adv, f2Adv };
});

// --- CHARTS ---
const renderCharts = () => {
  if (view.value === 'Fighter One Sheet' || view.value === 'Interesting Stats') {
    const metrics = getFighterMetrics(f1Selection.value);
    
    // Cumulative Head Trauma logic
    let currentSum = 0;
    const cumulative = metrics.raw.map(r => {
      const [hL] = String(r['HEAD'] || "0").split(' of ').map(v => parseInt(v));
      currentSum += hL;
      return currentSum;
    });

    const trace = {
      x: metrics.raw.map((_, i) => i + 1),
      y: cumulative,
      type: 'scatter', mode: 'lines+markers',
      fill: 'tozeroy', line: { color: '#ff4b4b' }
    };

    nextTick(() => {
      const el = document.getElementById('main-plot');
      if (el) Plotly.newPlot(el, [trace], { 
        title: 'Cumulative Head Strikes Absorbed',
        paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#fff' }, margin: { t: 40, b: 40, l: 40, r: 20 }
      });
    });
  }
};

watch([view, f1Selection], renderCharts);
onMounted(initData);
</script>

<template>
  <div class="ufc-container">
    <aside class="sidebar">
      <div class="logo">👊 UFC Stats</div>
      <nav>
        <button v-for="t in ['Welcome', 'Fighter One Sheet', 'Tale of the Tape', 'Interesting Stats']" 
                :key="t" :class="{ active: view === t }" @click="view = t">
          {{ t }}
        </button>
      </nav>
      <div class="footer-code">Built by Ilya</div>
    </aside>

    <main class="main-content">
      <div v-if="loading" class="loader">
        <div class="spin"></div>
        <p>Analyzing UFC History...</p>
      </div>

      <div v-else class="tab-view">
        <section v-if="view === 'Welcome'" class="welcome-box">
          <h1>UFC Stats Explorer v1.0</h1>
          <p>Explore the history of the octagon. Select a tab to start.</p>
          <img src="https://media.tenor.com/8jkYjD4cnqUAAAAM/just-bleed.gif" class="hero-gif" />
        </section>

        <section v-if="view === 'Fighter One Sheet'">
          <div class="selector-row">
            <select v-model="f1Selection">
              <option v-for="f in dataStore.fighterList" :key="f" :value="f">{{ f }}</option>
            </select>
          </div>
          <div class="metric-grid">
            <div class="card"><label>Head Movement</label><span>{{ getFighterMetrics(f1Selection).headMovement }}%</span></div>
            <div class="card"><label>Total Fights</label><span>{{ getFighterMetrics(f1Selection).fights }}</span></div>
            <div class="card"><label>TDs Landed</label><span>{{ getFighterMetrics(f1Selection).tdLanded }}</span></div>
          </div>
          <div id="main-plot"></div>
        </section>

        <section v-if="view === 'Tale of the Tape'">
          <div class="compare-container">
            <div class="fighter-pane">
              <select v-model="f1Selection"><option v-for="f in dataStore.fighterList" :value="f">{{ f }}</option></select>
              <div v-if="comparison.f1Adv > comparison.f2Adv" class="adv-tag">ADVANTAGE</div>
              <div class="big-stat">{{ comparison.f1.sigStr }} <small>Strikes</small></div>
            </div>

            <div class="vs-divider">VS</div>

            <div class="fighter-pane">
              <select v-model="f2Selection"><option v-for="f in dataStore.fighterList" :value="f">{{ f }}</option></select>
              <div v-if="comparison.f2Adv > comparison.f1Adv" class="adv-tag">ADVANTAGE</div>
              <div class="big-stat">{{ comparison.f2.sigStr }} <small>Strikes</small></div>
            </div>
          </div>
          <div class="summary-box">
            {{ comparison.f1Adv > comparison.f2Adv ? f1Selection : f2Selection }} has 
            {{ Math.abs(comparison.f1Adv - comparison.f2Adv) }} more advantages to win.
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style>
:root { --red: #ff4b4b; --bg: #0e1117; --sidebar: #262730; }
body { margin: 0; background: var(--bg); color: white; font-family: 'Inter', sans-serif; }

.ufc-container { display: flex; min-height: 100vh; }
.sidebar { width: 260px; background: var(--sidebar); padding: 20px; display: flex; flex-direction: column; }
.logo { font-size: 1.5rem; font-weight: bold; margin-bottom: 30px; color: var(--red); }
.sidebar button { 
  background: none; border: none; color: #ccc; text-align: left; 
  padding: 12px; font-size: 1rem; cursor: pointer; border-radius: 8px;
}
.sidebar button.active { background: #363742; color: white; border-left: 4px solid var(--red); }

.main-content { flex: 1; padding: 40px; }
.metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }
.card { background: var(--sidebar); padding: 20px; border-radius: 12px; text-align: center; }
.card label { display: block; font-size: 0.8rem; color: #888; margin-bottom: 10px; }
.card span { font-size: 1.8rem; font-weight: bold; }

.compare-container { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.vs-divider { font-size: 3rem; font-weight: 900; color: var(--red); font-style: italic; }
.fighter-pane { flex: 1; background: var(--sidebar); padding: 30px; border-radius: 15px; text-align: center; }
.adv-tag { background: #42b883; color: black; font-weight: bold; padding: 5px; margin-top: 10px; border-radius: 4px; }
.big-stat { font-size: 2.5rem; margin-top: 20px; }

select { width: 100%; padding: 12px; background: #0e1117; color: white; border: 1px solid #444; border-radius: 8px; }
.summary-box { margin-top: 40px; background: #1a1c23; padding: 20px; border-radius: 10px; text-align: center; font-size: 1.2rem; }
.hero-gif { width: 100%; max-width: 400px; border-radius: 10px; margin-top: 20px; }

.loader { text-align: center; margin-top: 100px; }
.spin { border: 4px solid #333; border-top-color: var(--red); width: 40px; height: 40px; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
