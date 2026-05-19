<template>
  <div class="dashboard">
    <section class="overview">
      <div class="card">
        <p class="label">今日订单</p>
        <h3>{{ overview.todayOrders }}</h3>
        <span>订单更新更及时</span>
      </div>
      <div class="card">
        <p class="label">今日营业额</p>
        <h3>¥{{ Number(overview.todayRevenue || 0).toFixed(2) }}</h3>
        <span>统计今日成交金额</span>
      </div>
      <div class="card">
        <p class="label">待发货</p>
        <h3>{{ overview.pendingOrders }}</h3>
        <span>优先处理</span>
      </div>
      <div class="card">
        <p class="label">已发货</p>
        <h3>{{ overview.shippedOrders }}</h3>
        <span>物流同步中</span>
      </div>
    </section>

    <section class="charts">
      <div class="card chart-card">
        <div class="chart-header">
          <div>
            <h3>近 7 天订单趋势</h3>
            <span>每日订单数量</span>
          </div>
          <span class="tag">折线图</span>
        </div>
        <div class="chart-body">
          <canvas ref="lineCanvas"></canvas>
        </div>
      </div>
      <div class="card chart-card">
        <div class="chart-header">
          <div>
            <h3>订单状态分布</h3>
            <span>待发货 vs 已发货</span>
          </div>
          <span class="tag warn">环形图</span>
        </div>
        <div class="chart-body">
          <canvas ref="doughnutCanvas"></canvas>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { Chart } from 'chart.js/auto'
import { fetchMerchantOverview } from '../../api'

const overview = reactive({
  todayOrders: 0,
  todayRevenue: 0,
  pendingOrders: 0,
  shippedOrders: 0,
  recentOrders: []
})

const lineCanvas = ref(null)
const doughnutCanvas = ref(null)
let lineChart = null
let doughnutChart = null

const buildLineChart = (data) => {
  if (!lineCanvas.value) return
  const labels = data.map((item) => item.date.slice(5))
  const values = data.map((item) => item.count)

  if (lineChart) {
    lineChart.data.labels = labels
    lineChart.data.datasets[0].data = values
    lineChart.update()
    return
  }

  lineChart = new Chart(lineCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: '订单数',
          data: values,
          borderColor: '#4f6cff',
          backgroundColor: 'rgba(79, 108, 255, 0.18)',
          tension: 0.35,
          fill: true,
          pointRadius: 3,
          pointBackgroundColor: '#4f6cff'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      layout: {
        padding: { left: 8, right: 8, bottom: 8 }
      },
      scales: {
        x: {
          grid: { display: false }
        },
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        }
      }
    }
  })
}

const buildDoughnutChart = (pending, shipped) => {
  if (!doughnutCanvas.value) return

  if (doughnutChart) {
    doughnutChart.data.datasets[0].data = [pending, shipped]
    doughnutChart.update()
    return
  }

  doughnutChart = new Chart(doughnutCanvas.value, {
    type: 'doughnut',
    data: {
      labels: ['待发货', '已发货'],
      datasets: [
        {
          data: [pending, shipped],
          backgroundColor: ['#f59e0b', '#4f6cff'],
          borderWidth: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { boxWidth: 10, padding: 12 }
        }
      },
      cutout: '72%'
    }
  })
}

const loadData = async () => {
  try {
    const data = await fetchMerchantOverview()
    Object.assign(overview, data)
    buildLineChart(data.recentOrders || [])
    buildDoughnutChart(data.pendingOrders || 0, data.shippedOrders || 0)
  } catch (error) {
    console.warn(error)
  }
}

onMounted(loadData)

onBeforeUnmount(() => {
  lineChart?.destroy()
  doughnutChart?.destroy()
})
</script>

<style scoped>
.dashboard {
  display: grid;
  gap: 28px;
}

.overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.card {
  background: var(--panel);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow);
}

.label {
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 13px;
}

.card h3 {
  margin: 0 0 8px;
  font-size: 26px;
}

.card span {
  color: var(--muted);
  font-size: 12px;
}

.charts {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.chart-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 260px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.chart-header h3 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #24365f;
}

.chart-header span {
  color: var(--muted);
  font-size: 12px;
}

.chart-body {
  flex: 1;
  min-height: 180px;
  position: relative;
}

.tag {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: #eef2ff;
  color: #5163ff;
  white-space: nowrap;
}

.tag.warn {
  background: #fff4e5;
  color: #f59e0b;
}

canvas {
  width: 100% !important;
  height: 100% !important;
}

@media (max-width: 960px) {
  .charts {
    grid-template-columns: 1fr;
  }
}
</style>
