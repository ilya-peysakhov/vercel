<script setup>
import { ref, computed } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale
} from 'chart.js';

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale);

// State for our data
const dataPoints = ref([10, 25, 45, 30, 60]);
const labels = ref(['Jan', 'Feb', 'Mar', 'Apr', 'May']);

const chartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: 'Learning Progress',
      backgroundColor: '#42b883',
      borderColor: '#42b883',
      data: dataPoints.value
    }
  ]
}));

const addData = () => {
  const months = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const nextMonth = months[labels.value.length - 5] || 'Next';
  
  labels.value.push(nextMonth);
  dataPoints.value.push(Math.floor(Math.random() * 100));
};
</script>

<template>
  <div class="container">
    <h1>My Vercel Vue App</h1>
    
    <button @click="addData">Add Random Data</button>

    <div class="chart-wrapper">
      <Line :data="chartData" />
    </div>
  </div>
</template>

<style scoped>
.container {
  font-family: sans-serif;
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
}

button {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 20px;
}

.chart-wrapper {
  height: 300px;
}
</style>
