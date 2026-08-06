/**
 * Generic trend line chart for income or expense trends.
 */
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

interface Props {
  data: Array<{ date: string; amount: number }>
  color?: 'green' | 'red' | 'blue' | 'purple'
  label?: string
  height?: number
}

const COLOR_MAP = {
  green: { border: 'rgba(16,185,129,1)', bg: 'rgba(16,185,129,0.1)' },
  red:   { border: 'rgba(239,68,68,1)',  bg: 'rgba(239,68,68,0.1)' },
  blue:  { border: 'rgba(59,130,246,1)', bg: 'rgba(59,130,246,0.1)' },
  purple:{ border: 'rgba(109,40,217,1)', bg: 'rgba(109,40,217,0.1)' },
}

export function TrendLineChart({ data, color = 'purple', label = 'Amount', height = 180 }: Props) {
  const { border, bg } = COLOR_MAP[color]

  const chartData = {
    labels: data.map((d) =>
      new Date(d.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })
    ),
    datasets: [{
      label,
      data: data.map((d) => d.amount),
      borderColor: border,
      backgroundColor: bg,
      fill: true,
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 4,
    }],
  }

  return (
    <div style={{ height }}>
      <Line
        data={chartData}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ₹${Number(ctx.raw).toLocaleString('en-IN')}`,
              },
            },
          },
          scales: {
            x: { grid: { display: false }, ticks: { font: { size: 9 }, maxTicksLimit: 10 } },
            y: {
              grid: { color: 'rgba(128,128,128,0.07)' },
              ticks: {
                font: { size: 10 },
                callback: (v) => `₹${Number(v) >= 1000 ? (Number(v)/1000).toFixed(0)+'K' : v}`,
              },
            },
          },
        }}
      />
    </div>
  )
}
