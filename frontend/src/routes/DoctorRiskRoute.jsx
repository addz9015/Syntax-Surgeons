import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { DataTable, Section } from '../components/ui'

export default function DoctorRiskRoute({ dashboard }) {
  return (
    <div className="content-grid">
      <Section title="Clinician exposure" subtitle="Highest composite risk prescribers">
        <div className="chart-shell tall">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dashboard.summary.doctors} margin={{ left: 10, right: 10, top: 8, bottom: 8 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
              <XAxis dataKey="Doctor_ID" stroke="#9fb3c8" />
              <YAxis stroke="#9fb3c8" />
              <Tooltip />
              <Bar dataKey="Composite_Risk_Score" radius={[8, 8, 0, 0]}>
                {dashboard.summary.doctors.map((entry, index) => (
                  <Cell
                    key={`${entry.Doctor_ID}-${index}`}
                    fill={{ GREEN: '#3d9970', AMBER: '#f0a202', RED: '#d1495b' }[entry.Risk_Tier] || '#0f8b8d'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Section>

      <Section title="Doctor risk table" subtitle="Top risk-profiled prescribers">
        <DataTable
          columns={Object.keys(dashboard.summary.doctors[0] || {}).map((key) => ({ key, label: key.replaceAll('_', ' ') }))}
          rows={dashboard.summary.doctors}
        />
      </Section>
    </div>
  )
}
