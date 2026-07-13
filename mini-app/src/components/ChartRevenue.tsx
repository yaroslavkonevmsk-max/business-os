import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { formatShortDate, formatCurrency } from '@/utils/formatters'

interface ChartRevenueProps {
  data: { date: string; amount: number }[]
}

export function ChartRevenue({ data }: ChartRevenueProps): JSX.Element {
  return (
    <div className="w-full h-48">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2481cc" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#2481cc" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
          <XAxis
            dataKey="date"
            tickFormatter={(v: string) => formatShortDate(v)}
            tick={{ fontSize: 10, fill: 'currentColor' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
            tick={{ fontSize: 10, fill: 'currentColor' }}
            axisLine={false}
            tickLine={false}
            width={40}
          />
          <Tooltip
            formatter={(value: number) => [formatCurrency(value), 'Выручка']}
            labelFormatter={(label: string) => formatShortDate(label)}
            contentStyle={{
              backgroundColor: 'var(--tg-secondary-bg-color)',
              border: 'none',
              borderRadius: '12px',
              color: 'var(--tg-text-color)',
            }}
          />
          <Area
            type="monotone"
            dataKey="amount"
            stroke="#2481cc"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorRevenue)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
