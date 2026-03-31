import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { DataTable, Section, formatNumber } from '../components/ui'

export default function QualityRoute({ dashboard }) {
  return (
    <div className="content-grid">
      <Section title="PRD performance" subtitle="KPI values compared to targets">
        <div className="chart-shell tall">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dashboard.summary.kpis} layout="vertical" margin={{ left: 24, right: 16, top: 8, bottom: 8 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.08)" horizontal={false} />
              <XAxis type="number" stroke="#9fb3c8" />
              <YAxis type="category" dataKey="KPI" width={170} stroke="#9fb3c8" />
              <Tooltip />
              <Bar dataKey="Value" radius={[0, 8, 8, 0]}>
                {dashboard.summary.kpis.map((entry, index) => (
                  <Cell key={`${entry.KPI}-${index}`} fill={entry.Pass ? '#0f8b8d' : '#d1495b'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Section>

      <Section title="Data quality monitor" subtitle="Scorecard metrics from pipeline validation">
        <DataTable
          columns={[
            { key: 'metric', label: 'Metric' },
            {
              key: 'value',
              label: 'Value',
              render: (row) => (typeof row.value === 'number' ? formatNumber(row.value, 3) : String(row.value)),
            },
          ]}
          rows={dashboard.qualityRows}
        />
      </Section>
    </div>
  )
}
