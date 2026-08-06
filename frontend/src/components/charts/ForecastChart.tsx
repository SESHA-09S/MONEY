/**
 * Forecast chart with confidence band (upper/lower bounds).
 */
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import type { ForecastPoint } from '@/types'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

interface Props {
  data: ForecastPoint[]
  height?: number
}

export function ForecastChart({ data, height = 280 }: Props) {
  const labels = data.map((d) =>
    new Date(d.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })
  )

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Predicted',
        data: data.map((d) => d.predicted),
        borderColor: 'rgba(109, 40, 217, 1)',
        backgroundColor: 'rgba(109, 40, 217, 0.12)',
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5,
      },
      {
        label: 'Upper Bound',
        data: data.map((d) => d.upper),
        borderColor: 'rgba(109, 40, 217, 0.25)',
        borderDash: [5, 5],
        fill: false,
        tension: 0.4,
        pointRadius: 0,
      },
      {
        label: 'Lower Bound',
        data: data.map((d) => d.lower),
        borderColor: 'rgba(109, 40, 217, 0.25)',
        borderDash: [5, 5],
        fill: '-1',
        backgroundColor: 'rgba(109, 40, 217, 0.04)',
        tension: 0.4,
        pointRadius: 0,
      },
    ],
  }

  return (
    <div style={{ height }}>
      <Line
        data={chartData}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          plugins: {
            legend: { position: 'top', labels: { font: { size: 11 }, boxWidth: 14 } },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.dataset.label}: ₹${Number(ctx.raw).toLocaleString('en-IN')}`,
              },
            },
          },
          scales: {
            x: { grid: { display: false }, ticks: { font: { size: 10 }, maxTicksLimit: 12 } },
            y: {
              grid: { color: 'rgba(128,128,128,0.08)' },
              ticks: {
                font: { size: 11 },
                callback: (val) => `₹${Number(val) >= 1000 ? (Number(val) / 1000).toFixed(0) + 'K' : val}`,
              },
            },
          },
        }}
      />
    </div>
  )
}
