import { Section, formatNumber } from '../components/ui'

export default function PrescribingRoute({ dashboard }) {
  return (
    <div className="content-grid split-two">
      <Section title="Dataset prescribing simulator" subtitle="Run the original what-if engine">
        <div className="control-stack">
          <label>
            Patient
            <select value={dashboard.selectedPatient} onChange={(event) => dashboard.setSelectedPatient(event.target.value)}>
              {dashboard.summary.patients.map((patient) => (
                <option key={`sim-${patient.Patient_ID}`} value={patient.Patient_ID}>
                  {patient.Patient_ID}
                </option>
              ))}
            </select>
          </label>
          <label>
            Medicine
            <select value={dashboard.selectedMedicine} onChange={(event) => dashboard.setSelectedMedicine(event.target.value)}>
              {dashboard.summary.medicines.map((medicine) => (
                <option key={medicine.Medicine_ID} value={medicine.Medicine_ID}>
                  {medicine.Medicine_ID} - {medicine.Medicine_Name} - {medicine.Allergen_Class}
                </option>
              ))}
            </select>
          </label>
          <button
            className="primary-button"
            onClick={dashboard.runSimulation}
            disabled={dashboard.simulating || !dashboard.selectedPatient || !dashboard.selectedMedicine}
          >
            {dashboard.simulating ? 'Running simulation...' : 'Run safety simulation'}
          </button>
        </div>

        {dashboard.selectedMedicineSummary ? (
          <div className="medicine-card">
            <strong>{dashboard.selectedMedicineSummary.Medicine_Name}</strong>
            <span>{dashboard.selectedMedicineSummary.Allergen_Class}</span>
            <span>
              Requires allergy check:{' '}
              {String(dashboard.selectedMedicineSummary.Requires_Allergy_Check).toLowerCase() === 'true' ? 'Yes' : 'No'}
            </span>
          </div>
        ) : null}

        {dashboard.simulation ? (
          <div className="simulation-result">
            <div className="risk-ring">
              <span>{formatNumber(dashboard.simulation.risk_score * 100, 1)}%</span>
              <small>Estimated risk</small>
            </div>
            <div className="simulation-copy">
              <h3>{dashboard.simulation.conflict.conflict}</h3>
              <p>{dashboard.simulation.conflict.reason}</p>
              <p>ABS score: {formatNumber(dashboard.simulation.abs_score, 1)}</p>
            </div>
          </div>
        ) : null}
      </Section>

      <Section title="Custom allergy detection" subtitle="Enter user data and test a new prescription for allergy reaction risk">
        <div className="control-stack single-col">
          <label>
            Patient label
            <input value={dashboard.customPatientLabel} onChange={(event) => dashboard.setCustomPatientLabel(event.target.value)} />
          </label>
          <label>
            Prescription medicine name
            <input
              value={dashboard.customMedicineName}
              onChange={(event) => dashboard.setCustomMedicineName(event.target.value)}
              placeholder="e.g. Amoxicillin 500mg"
            />
          </label>
          <label>
            Prescription allergen class
            <input
              value={dashboard.customMedicineClass}
              onChange={(event) => dashboard.setCustomMedicineClass(event.target.value)}
              placeholder="e.g. Beta-Lactam"
            />
          </label>
          <label>
            Optional ABS score (leave blank for automatic estimate)
            <input
              type="number"
              min="0"
              max="100"
              value={dashboard.customAbsScore}
              onChange={(event) => dashboard.setCustomAbsScore(event.target.value)}
            />
          </label>
          <label className="check-label">
            <input
              type="checkbox"
              checked={dashboard.customRequiresCheck}
              onChange={(event) => dashboard.setCustomRequiresCheck(event.target.checked)}
            />
            Medicine requires allergy check
          </label>
          <label>
            Allergies (one line each: allergen_name|allergen_class|severity|status)
            <textarea value={dashboard.customAllergiesText} onChange={(event) => dashboard.setCustomAllergiesText(event.target.value)} rows={6} />
          </label>
          <button className="primary-button" onClick={dashboard.runCustomSimulation} disabled={dashboard.runningCustomSimulation}>
            {dashboard.runningCustomSimulation ? 'Checking allergy risk...' : 'Detect allergic reaction risk'}
          </button>
        </div>

        {dashboard.customSimulation ? (
          <div className="simulation-result">
            <div className="risk-ring">
              <span>{formatNumber(dashboard.customSimulation.risk_score * 100, 1)}%</span>
              <small>Estimated risk</small>
            </div>
            <div className="simulation-copy">
              <h3>{dashboard.customSimulation.conflict.conflict}</h3>
              <p>{dashboard.customSimulation.conflict.reason}</p>
              <p>ABS score used: {formatNumber(dashboard.customSimulation.abs_score, 1)}</p>
              <p>Prescription: {dashboard.customSimulation.medicine_name}</p>
            </div>
          </div>
        ) : null}
      </Section>
    </div>
  )
}
