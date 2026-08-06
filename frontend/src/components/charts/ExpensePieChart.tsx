/**
 * Expense breakdown doughnut chart.
 */
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'react-chartjs-2'
import { formatCompact } from '@/lib/utils'

ChartJS.register(ArcElement, Tooltip, Legend)

const COLORS = [
  '#6d28d9', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#06b6d4', '#84cc16', '#f97316', '#ec4899',
]

interface Props {
  data: Array<{ name: string; value: number }>
  height?: number
}

export function ExpensePieChart({ data, height = 200 }: Props) {
  const chartData = {
    labels: data.map((d) => d.name.replace(/_/g, ' ')),
    datasets: [{
      data: data.map((d) => d.value),
      backgroundColor: COLORS.slice(0, data.length),
      borderWidth: 0,
      hoverBorderWidth: 3,
      hoverBorderColor: '#fff',
    }],
  }

  return (
    <div>
      <div style={{ height }}>
        <Doughnut
          data={chartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            cutout: '68%',
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: (ctx) => ` ${ctx.label}: ${formatCompact(ctx.raw as number)}`,
                },
              },
            },
          }}
        />
      </div>
      <div className="mt-3 space-y-1.5">
        {data.slice(0, 6).map((item, i) => (
          <div key={item.name} className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: COLORS[i] }} />
              <span className="text-muted-foreground capitalize truncate max-w-[120px]">
                {item.name.replace(/_/g, ' ')}
              </span>
            </div>
            <span className="font-semibold ml-2">{formatCompact(item.value)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
