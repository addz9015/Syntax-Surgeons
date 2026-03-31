import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from 'recharts'
import { DataTable, Section, formatNumber } from '../components/ui'

export default function ClusterRoute({ dashboard }) {
  return (
    <div className="content-grid">
      <Section title="Signal landscape" subtitle="IgE against allergy burden score">
        <div className="chart-shell tall">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ left: 8, right: 16, top: 8, bottom: 8 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.08)" />
              <XAxis type="number" dataKey="x" name="IgE" stroke="#9fb3c8" />
              <YAxis type="number" dataKey="y" name="ABS" stroke="#9fb3c8" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} formatter={(value) => formatNumber(value)} />
              <Scatter data={dashboard.clusterScatter} fill="#7bdff2" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </Section>

      <Section title="Cluster summary" subtitle="Segment-level averages from the analytics pipeline">
        <DataTable
          columns={Object.keys(dashboard.summary.clusters[0] || {}).map((key) => ({ key, label: key.replaceAll('_', ' ') }))}
          rows={dashboard.summary.clusters}
        />
      </Section>
    </div>
  )
}
