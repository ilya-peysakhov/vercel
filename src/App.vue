<script setup>
import { ref, computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale)

const dataPoints = ref([10, 20, 30])
const labels = ref(['A', 'B', 'C'])

const chartData = computed(() => ({
  labels: labels.value,
  datasets: [{
    label: 'Data',
    backgroundColor: '#42b883',
    data: dataPoints.value
  }]
}))

const addData = () => {
  labels.value.push('D')
  dataPoints.value.push(50)
}
</script>

<template>
  <div style="text-align: center; font-family: sans-serif;">
    <h1>Vue Chart App</h1>
    <button @click="addData">Add Data</button>
    <div style="max-width: 500px; margin: auto;">
      <Line :data="chartData" />
    </div>
  </div>
</template>
