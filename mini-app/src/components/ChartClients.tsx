import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface ChartClientsProps {
  data: { period: string; new_clients: number; repeat_clients: number }[]
}

export function ChartClients({ data }: ChartClientsProps): JSX.Element {
  return (
    <div className="w-full h-56">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
          <XAxis
            dataKey="period"
            tick={{ fontSize: 10, fill: 'currentColor' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 10, fill: 'currentColor' }}
            axisLine={false}
            tickLine={false}
            width={30}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--tg-secondary-bg-color)',
              border: 'none',
              borderRadius: '12px',
              color: 'var(--tg-text-color)',
            }}
          />
          <Legend
            formatter={(value: string) => (
              <span className="text-xs text-tg-text">
                {value === 'new_clients' ? 'Новые' : 'Повторные'}
              </span>
            )}
          />
          <Bar dataKey="new_clients" fill="#10b981" radius={[4, 4, 0, 0]} />
          <Bar dataKey="repeat_clients" fill="#3b82f6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
