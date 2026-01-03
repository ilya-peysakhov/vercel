<script setup>
import { ref, onMounted, computed, markRaw, nextTick } from 'vue';
import Papa from 'papaparse';
import Plotly from 'plotly.js-dist-min';

const view = ref('Welcome');
const loading = ref(true);
const loadingProgress = ref(0);

// Optimization 1: Use markRaw so Vue doesn't track every single row for changes
const dataStore = ref({
  stats: markRaw([]),
  fighterMap: markRaw(new Map()), // Optimization 2: Pre-indexed lookup
  fighterList: []
});

const f1Selection = ref('Jon Jones');
const f2Selection = ref('Stipe Miocic');

const DATA_URLS = {
  stats: "https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_fight_stats.csv",
};

// High-performance data initialization
const initData = async () => {
  loading.value = true;
  
  Papa.parse(DATA_URLS.stats, {
    download: true,
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    chunk: (results) => {
      // Optional: Track progress if the file is massive
    },
    complete: (results) => {
      const rows = results.data;
      const lookup = new Map();
      const names = new Set();

      // We process the loop ONCE to build our index
      for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        if (!row.FIGHTER) continue;
        
        const name = row.FIGHTER.trim();
        names.add(name);

        if (!lookup.has(name)) {
          lookup.set(name, []);
        }
        lookup.get(name).push(row);
      }

      dataStore.value.stats = markRaw(rows);
      dataStore.value.fighterMap = markRaw(lookup);
      dataStore.value.fighterList = Array.from(names).sort();
      
      loading.value = false;
    }
  });
};

// Optimization 3: Computed metrics now use the Map (Instant lookup)
const getFighterMetrics = (name) => {
  const fStats = dataStore.value.fighterMap.get(name) || [];
  if (fStats.length === 0) return { sigStrDiff: 0, fights: 0, kd: 0 };

  let landed = 0;
  let kd = 0;
  const bouts = new Set();

  for (const s of fStats) {
    landed += parseInt(String(s['SIG.STR.']).split(' of ')[0]) || 0;
    kd += s.KD || 0;
    bouts.add(s.BOUT);
  }

  return {
    sigStrLanded: landed,
    kd,
    fights: bouts.size,
    raw: fStats
  };
};

// Tale of the Tape Logic (now nearly instant)
const comparison = computed(() => {
  const m1 = getFighterMetrics(f1Selection.value);
  const m2 = getFighterMetrics(f2Selection.value);
  
  // You can expand this with your Streamlit logic (td_rate, etc.)
  return {
    f1: m1,
    f2: m2,
    f1Adv: (m1.sigStrLanded > m2.sigStrLanded ? 1 : 0) + (m1.kd > m2.kd ? 1 : 0),
    f2Adv: (m2.sigStrLanded > m1.sigStrLanded ? 1 : 0) + (m2.kd > m1.kd ? 1 : 0)
  };
});

onMounted(initData);
</script>
