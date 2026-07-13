import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { formatCurrency } from '@/utils/formatters'

interface ChartExpensesProps {
  data: { category: string; amount: number }[]
}

const COLORS = ['#f59e0b', '#ef4444', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4', '#6366f1']

const categoryLabels: Record<string, string> = {
  rent: 'Аренда',
  software: 'Программы',
  hardware: 'Оборудование',
  transport: 'Транспорт',
  marketing: 'Маркетинг',
  office: 'Офис',
  taxes: 'Налоги',
  salary: 'Зарплата',
  other: 'Прочее',
}

export function ChartExpenses({ data }: ChartExpensesProps): JSX.Element {
  const chartData = data.map((item) => ({
    name: categoryLabels[item.category] || item.category,
    value: item.amount,
  }))

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={4}
            dataKey="value"
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => formatCurrency(value)}
            contentStyle={{
              backgroundColor: 'var(--tg-secondary-bg-color)',
              border: 'none',
              borderRadius: '12px',
              color: 'var(--tg-text-color)',
            }}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            iconSize={8}
            formatter={(value: string) => <span className="text-xs text-tg-text">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
