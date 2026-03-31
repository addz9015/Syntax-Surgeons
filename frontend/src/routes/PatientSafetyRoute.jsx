import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { DataTable, Section, StatCard, formatNumber } from '../components/ui'

export default function PatientSafetyRoute({ dashboard }) {
  return (
    <div className="content-grid split-two">
      <Section title="Patient console" subtitle="Profile, allergy history, and recent prescriptions">
        <div className="control-row">
          <label>
            Patient
            <select value={dashboard.selectedPatient} onChange={(event) => dashboard.setSelectedPatient(event.target.value)}>
              {dashboard.summary.patients.map((patient) => (
                <option key={patient.Patient_ID} value={patient.Patient_ID}>
                  {patient.Patient_ID} - {patient.Cluster_Label}
                </option>
              ))}
            </select>
          </label>
          {dashboard.selectedPatientSummary ? (
            <div className="patient-banner">
              <strong>{dashboard.selectedPatientSummary.Patient_ID}</strong>
              <span>{dashboard.selectedPatientSummary.ABS_Risk_Band} risk</span>
              <span>ABS {formatNumber(dashboard.selectedPatientSummary.Allergy_Burden_Score, 1)}</span>
            </div>
          ) : null}
        </div>

        <div className="mini-stats">
          <StatCard
            label="IgE average"
            value={dashboard.selectedPatientSummary ? formatNumber(dashboard.selectedPatientSummary.IgE_Level_Avg, 1) : '...'}
            hint="lab-derived immunology signal"
          />
          <StatCard
            label="Allergen classes"
            value={dashboard.selectedPatientSummary ? String(dashboard.selectedPatientSummary.Active_Allergen_Class_Count) : '...'}
            hint="active burden count"
          />
          <StatCard
            label="Comorbidities"
            value={dashboard.selectedPatientSummary ? String(dashboard.selectedPatientSummary.Comorbidity_Count) : '...'}
            hint="complexity factor"
          />
        </div>

        <h3 className="subheading">Allergy profile</h3>
        <DataTable
          columns={[
            { key: 'Allergen_Name', label: 'Allergen' },
            { key: 'Allergen_Class', label: 'Class' },
            { key: 'Severity', label: 'Severity' },
            { key: 'Is_Current', label: 'Current' },
            { key: 'Reaction_Type', label: 'Reaction' },
          ]}
          rows={dashboard.patientProfile?.allergies || []}
        />

        <h3 className="subheading">Recent prescriptions</h3>
        <DataTable
          columns={[
            { key: 'Prescription_ID', label: 'Prescription' },
            { key: 'Medicine_Name', label: 'Medicine' },
            { key: 'Allergen_Class', label: 'Class' },
            { key: 'Conflict_Detected', label: 'Conflict' },
            { key: 'Override_Issued', label: 'Override' },
            { key: 'Prescription_Date', label: 'Date' },
          ]}
          rows={dashboard.patientProfile?.prescriptions || []}
        />
      </Section>

      <Section title="Risk mix" subtitle="Current patient burden by ABS band">
        <div className="chart-shell">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={dashboard.riskMix} dataKey="value" nameKey="name" innerRadius={70} outerRadius={108} paddingAngle={3}>
                {dashboard.riskMix.map((entry) => (
                  <Cell
                    key={entry.name}
                    fill={{ LOW: '#3d9970', MODERATE: '#f0a202', HIGH: '#f18805', CRITICAL: '#d95d39' }[entry.name] || '#4f6d7a'}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Section>
    </div>
  )
}
