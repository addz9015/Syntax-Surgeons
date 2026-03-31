import { useEffect, useMemo, useState } from 'react'
import { apiGet, apiPost, API_BASE_URL } from '../lib/api'

function parseCustomAllergies(customAllergiesText) {
  return customAllergiesText
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [allergenName, allergenClass, severity, status] = line.split('|').map((part) => part.trim())
      return {
        allergen_name: allergenName || '',
        allergen_class: allergenClass || '',
        severity: (severity || 'UNKNOWN').toUpperCase(),
        status: (status || 'current').toLowerCase(),
      }
    })
}

export function useDashboardData() {
  const [health, setHealth] = useState({ label: 'Checking', detail: 'starting', url: API_BASE_URL })
  const [summary, setSummary] = useState({
    kpis: [],
    model: null,
    quality: null,
    doctors: [],
    clusters: [],
    patients: [],
    medicines: [],
    explanations: [],
  })
  const [selectedPatient, setSelectedPatient] = useState('')
  const [selectedMedicine, setSelectedMedicine] = useState('')
  const [patientProfile, setPatientProfile] = useState(null)
  const [simulation, setSimulation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [simulating, setSimulating] = useState(false)
  const [customPatientLabel, setCustomPatientLabel] = useState('Custom patient')
  const [customMedicineName, setCustomMedicineName] = useState('')
  const [customMedicineClass, setCustomMedicineClass] = useState('')
  const [customRequiresCheck, setCustomRequiresCheck] = useState(true)
  const [customAbsScore, setCustomAbsScore] = useState('')
  const [customAllergiesText, setCustomAllergiesText] = useState('Penicillin allergy|Beta-Lactam|SEVERE|current')
  const [customSimulation, setCustomSimulation] = useState(null)
  const [runningCustomSimulation, setRunningCustomSimulation] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadDashboard() {
      try {
        setLoading(true)
        const [healthData, kpis, model, quality, doctors, clusters, patients, medicines, explanations] = await Promise.all([
          apiGet('/health'),
          apiGet('/kpis'),
          apiGet('/model-metrics'),
          apiGet('/data-quality'),
          apiGet('/doctor-risk?limit=12'),
          apiGet('/clusters'),
          apiGet('/patients?limit=500'),
          apiGet('/medicines?limit=500'),
          apiGet('/explanations?limit=6'),
        ])

        if (cancelled) {
          return
        }

        setHealth({ label: 'Online', detail: healthData.status || 'ok', url: API_BASE_URL })
        setSummary({ kpis, model, quality, doctors, clusters, patients, medicines, explanations })
        setSelectedPatient((current) => current || String(patients[0]?.Patient_ID || ''))
        setSelectedMedicine((current) => current || String(medicines[0]?.Medicine_ID || ''))
        setError('')
      } catch (loadError) {
        if (!cancelled) {
          setHealth({ label: 'Offline', detail: 'unreachable', url: API_BASE_URL })
          setError(loadError.message)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadDashboard()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!selectedPatient) {
      return
    }

    let cancelled = false

    async function loadPatient() {
      try {
        const profile = await apiGet(`/patients/${encodeURIComponent(selectedPatient)}`)
        if (!cancelled) {
          setPatientProfile(profile)
        }
      } catch (profileError) {
        if (!cancelled) {
          setError(profileError.message)
        }
      }
    }

    loadPatient()
    return () => {
      cancelled = true
    }
  }, [selectedPatient])

  async function runSimulation() {
    if (!selectedPatient || !selectedMedicine) {
      return
    }

    try {
      setSimulating(true)
      const result = await apiGet(
        `/simulate?patient_id=${encodeURIComponent(selectedPatient)}&medicine_id=${encodeURIComponent(selectedMedicine)}`,
      )
      setSimulation(result)
      setError('')
    } catch (simulationError) {
      setError(simulationError.message)
    } finally {
      setSimulating(false)
    }
  }

  async function runCustomSimulation() {
    try {
      setRunningCustomSimulation(true)
      const allergies = parseCustomAllergies(customAllergiesText)
      const payload = {
        patient_label: customPatientLabel,
        medicine_name: customMedicineName,
        medicine_allergen_class: customMedicineClass,
        requires_allergy_check: customRequiresCheck,
        allergies,
      }
      if (customAbsScore !== '') {
        payload.abs_score = Number(customAbsScore)
      }
      const result = await apiPost('/simulate-custom', payload)
      setCustomSimulation(result)
      setError('')
    } catch (customError) {
      setError(customError.message)
    } finally {
      setRunningCustomSimulation(false)
    }
  }

  const riskMix = useMemo(() => {
    const counts = new Map()
    summary.patients.forEach((patient) => {
      const band = patient.ABS_Risk_Band || 'UNKNOWN'
      counts.set(band, (counts.get(band) || 0) + 1)
    })
    return Array.from(counts.entries()).map(([name, value]) => ({ name, value }))
  }, [summary.patients])

  const clusterScatter = useMemo(
    () =>
      summary.patients.map((patient) => ({
        x: Number(patient.IgE_Level_Avg || 0),
        y: Number(patient.Allergy_Burden_Score || 0),
        z: Number(patient.Active_Allergen_Class_Count || 1),
        label: patient.Patient_ID,
      })),
    [summary.patients],
  )

  const selectedPatientSummary = summary.patients.find((patient) => String(patient.Patient_ID) === selectedPatient)
  const selectedMedicineSummary = summary.medicines.find((medicine) => String(medicine.Medicine_ID) === selectedMedicine)

  const qualityRows = useMemo(() => {
    if (!summary.quality) {
      return []
    }
    return Object.entries(summary.quality).map(([metric, value]) => ({ metric, value }))
  }, [summary.quality])

  return {
    health,
    summary,
    selectedPatient,
    setSelectedPatient,
    selectedMedicine,
    setSelectedMedicine,
    patientProfile,
    simulation,
    loading,
    error,
    simulating,
    customPatientLabel,
    setCustomPatientLabel,
    customMedicineName,
    setCustomMedicineName,
    customMedicineClass,
    setCustomMedicineClass,
    customRequiresCheck,
    setCustomRequiresCheck,
    customAbsScore,
    setCustomAbsScore,
    customAllergiesText,
    setCustomAllergiesText,
    customSimulation,
    runningCustomSimulation,
    runSimulation,
    runCustomSimulation,
    riskMix,
    clusterScatter,
    selectedPatientSummary,
    selectedMedicineSummary,
    qualityRows,
  }
}
