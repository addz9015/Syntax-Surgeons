import { CartesianGrid, Legend, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from 'recharts'
import { DataTable, Section, formatNumber } from '../components/ui'

const CLUSTER_COLORS = ['#7bdff2', '#f9c74f', '#f94144', '#43aa8b']

export default function ClusterRoute({ dashboard }) {
  const clusterEntries = Object.entries(dashboard.clusterScatter)

  return (
    <div className="content-grid">
      <Section title="Signal landscape" subtitle="ABS base score against allergy burden score, coloured by cluster">
        <div className="chart-shell tall">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ left: 8, right: 24, top: 8, bottom: 24 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.08)" />
              <XAxis
                type="number"
                dataKey="x"
                name="ABS Base Score"
                stroke="#9fb3c8"
                label={{ value: 'ABS Base Score', position: 'insideBottom', offset: -12, fill: '#9fb3c8', fontSize: 11 }}
              />
              <YAxis
                type="number"
                dataKey="y"
                name="Allergy Burden Score"
                stroke="#9fb3c8"
                label={{ value: 'Burden Score', angle: -90, position: 'insideLeft', fill: '#9fb3c8', fontSize: 11 }}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} formatter={(value, name) => [formatNumber(value), name]} />
              <Legend verticalAlign="top" wrapperStyle={{ fontSize: 12 }} />
              {clusterEntries.map(([label, data], i) => (
                <Scatter key={label} name={label} data={data} fill={CLUSTER_COLORS[i % CLUSTER_COLORS.length]} opacity={0.75} />
              ))}
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
