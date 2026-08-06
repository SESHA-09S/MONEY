/**
 * Reusable Cash Flow chart — income vs expense bar chart.
 */
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

interface DataPoint {
  date: string
  income: number
  expense: number
  net: number
}

interface Props {
  data: DataPoint[]
  height?: number
}

export function CashFlowChart({ data, height = 280 }: Props) {
  const labels = data.map((d) =>
    new Date(d.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })
  )

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Income',
        data: data.map((d) => d.income),
        backgroundColor: 'rgba(16, 185, 129, 0.85)',
        borderRadius: 4,
        borderSkipped: false,
      },
      {
        label: 'Expense',
        data: data.map((d) => d.expense),
        backgroundColor: 'rgba(239, 68, 68, 0.85)',
        borderRadius: 4,
        borderSkipped: false,
      },
    ],
  }

  return (
    <div style={{ height }}>
      <Bar
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
            x: { grid: { display: false }, ticks: { font: { size: 10 }, maxTicksLimit: 15 } },
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
