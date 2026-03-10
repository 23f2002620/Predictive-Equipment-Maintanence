<template>
  <div style="padding:32px 28px; background:var(--white); min-height:100vh;">

    <div class="fade-up" style="display:flex; align-items:flex-start; gap:14px; margin-bottom:28px; flex-wrap:wrap;">
      <RouterLink to="/" class="btn-secondary" style="padding:8px 12px; font-size:13px; flex-shrink:0;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
        Back
      </RouterLink>
      <div style="flex:1;">
        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:4px;">
          <h1 style="font-size:26px; font-weight:800; color:var(--gray-900); letter-spacing:-0.5px;">{{ machineId }}</h1>
          <RiskBadge v-if="risk" :code="risk.risk_code" />
        </div>
        <p style="font-size:13px; color:var(--gray-400); font-weight:400;">
          {{ isMRI ? 'Siemens MAGNETOM Vida · 3T Superconducting MRI' : 'GE Healthcare Revolution CT · Multi-Slice Scanner' }}
        </p>
      </div>
      <button @click="runAgent" :disabled="running" class="btn-primary" style="font-size:12px; flex-shrink:0;">
        <div v-if="running" class="spinner" style="width:12px; height:12px; border-top-color:white; border-color:rgba(255,255,255,0.3); border-width:1.5px;"></div>
        {{ running ? 'Running…' : '⚡ Run Agent' }}
      </button>
    </div>

    <div v-if="loading" style="display:flex; align-items:center; justify-content:center; height:300px;">
      <div class="spinner" style="width:28px; height:28px; border-width:2.5px;"></div>
    </div>

    <template v-else>

      <div v-if="risk" class="fade-up fade-up-1" style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:20px;">
        <StatCard label="Risk Level"      :value="risk.risk_label"                                           :color="riskColor"  />
        <StatCard label="Days to Failure" :value="risk.days_to_failure >= 999 ? '∞' : `${risk.days_to_failure}d`" :color="daysColor"  />
        <StatCard label="Confidence"      :value="`${(risk.confidence * 100).toFixed(0)}%`"                  color="var(--blue)" />
        <StatCard label="Anomaly / 7d"    :value="String(risk.anomaly_count_last7d)"                         :color="risk.anomaly_count_last7d > 3 ? 'var(--red)' : 'var(--amber)'" />
      </div>

      <div class="fade-up fade-up-2" style="display:grid; grid-template-columns:1fr auto; gap:16px; margin-bottom:20px; align-items:start;">
        <div v-if="risk" class="card" style="padding:20px;">
          <p style="font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700; margin-bottom:8px;">Agent Reasoning</p>
          <p style="font-size:13.5px; color:var(--gray-700); line-height:1.7; font-weight:400;">{{ risk.reasoning }}</p>
          <div v-if="risk.flagged_parameters?.length" style="display:flex; flex-wrap:wrap; gap:5px; margin-top:12px;">
            <span v-for="f in risk.flagged_parameters" :key="f.parameter"
              style="padding:3px 10px; font-size:11px; border-radius:980px; font-weight:600;"
              :style="f.severity === 'CRITICAL'
                ? 'background:var(--red-light); color:#c0392b; border:1px solid rgba(255,59,48,0.15);'
                : 'background:var(--amber-light); color:#b86e00; border:1px solid rgba(255,159,10,0.15);'">
              {{ f.parameter.replace(/_/g, ' ') }} (z={{ f.z_score }})
            </span>
          </div>
        </div>
        <div v-if="risk?.cost_impact" class="card" style="padding:20px; min-width:190px;">
          <p style="font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700; margin-bottom:12px;">Cost Impact</p>
          <div style="display:flex; flex-direction:column; gap:10px;">
            <div style="padding:12px; background:var(--green-light); border-radius:var(--radius-md); border:1px solid rgba(52,199,89,0.15); text-align:center;">
              <p style="font-size:10px; color:#1a7f3c; font-weight:700;">PREVENTIVE</p>
              <p style="font-size:20px; font-weight:800; color:#1a7f3c; letter-spacing:-0.5px; margin-top:3px;">₹{{ fmt(risk.cost_impact.preventive_cost_inr) }}</p>
            </div>
            <div style="padding:12px; background:var(--red-light); border-radius:var(--radius-md); border:1px solid rgba(255,59,48,0.15); text-align:center;">
              <p style="font-size:10px; color:#c0392b; font-weight:700;">BREAKDOWN</p>
              <p style="font-size:20px; font-weight:800; color:#c0392b; letter-spacing:-0.5px; margin-top:3px;">₹{{ fmt(risk.cost_impact.total_breakdown_cost_inr) }}</p>
            </div>
            <div style="padding:8px 12px; background:var(--gray-50); border-radius:var(--radius-sm); text-align:center; border:1px solid var(--gray-100);">
              <p style="font-size:11px; color:var(--green); font-weight:700;">Save ₹{{ fmt(risk.cost_impact.net_saving_inr) }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="card fade-up fade-up-3" style="padding:22px; margin-bottom:20px;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; flex-wrap:wrap; gap:10px;">
          <div style="display:flex; align-items:center; gap:8px;">
            <div style="width:30px; height:30px; border-radius:8px; background:var(--blue-light); display:flex; align-items:center; justify-content:center;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <h3 style="font-size:15px; font-weight:700; color:var(--gray-900); letter-spacing:-0.2px;">Sensor Trends — 30 Days</h3>
          </div>
          <div style="display:flex; gap:4px; background:var(--gray-100); border-radius:8px; padding:3px; flex-wrap:wrap;">
            <button v-for="s in sensors" :key="s.key" @click="selectSensor(s.key)"
              style="padding:5px 14px; border-radius:6px; font-size:12px; cursor:pointer; transition:all 0.2s var(--ease-out); border:none; font-weight:600; font-family:'Manrope',sans-serif;"
              :style="activeSensor === s.key
                ? 'background:white; color:var(--gray-900); box-shadow:var(--shadow-sm);'
                : 'background:transparent; color:var(--gray-500);'">
              {{ s.label }}
            </button>
          </div>
        </div>
        <div v-if="chartLoading" style="height:130px; display:flex; align-items:center; justify-content:center;">
          <div class="spinner"></div>
        </div>
        <SensorSparkline v-else :data="chartData" />
        <div style="display:flex; gap:20px; margin-top:10px; font-size:11px; color:var(--gray-400); font-weight:500;">
          <span style="display:flex; align-items:center; gap:5px;">
            <span style="display:inline-block; width:20px; height:2px; background:var(--blue); border-radius:1px;"></span>Value
          </span>
          <span style="display:flex; align-items:center; gap:5px;">
            <span style="display:inline-block; width:20px; height:1px; border-top:1px dashed rgba(0,113,227,0.35);"></span>Baseline
          </span>
          <span style="display:flex; align-items:center; gap:5px;">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--red);"></span>Anomaly
          </span>
        </div>
      </div>

      <div v-if="latest" class="card fade-up fade-up-4" style="padding:22px; margin-bottom:20px;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; flex-wrap:wrap; gap:8px;">
          <h3 style="font-size:15px; font-weight:700; color:var(--gray-900); letter-spacing:-0.2px;">Latest Readings</h3>
          <span style="font-size:11px; color:var(--gray-400); background:var(--gray-100); padding:5px 12px; border-radius:980px; font-weight:600;">{{ latest.date }}</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(155px,1fr)); gap:10px;">
          <div v-for="item in telemetryFields" :key="item.key" class="stat-surface" style="padding:12px 14px;">
            <p style="font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700; margin-bottom:5px;">{{ item.label }}</p>
            <!-- FIX: was `${v}${u}` giving "3.00T" — now `${v} ${u}` giving "3.00 T" -->
            <p style="font-size:16px; font-weight:800; letter-spacing:-0.3px; line-height:1;" :style="{ color: item.col }">
              {{ fmtVal(latest[item.key], item.unit) }}
            </p>
          </div>
        </div>
      </div>

      <Transition name="slide">
        <div v-if="agentResult" class="card fade-in" style="padding:22px;">
          <h3 style="font-size:15px; font-weight:700; color:var(--gray-900); margin-bottom:14px; letter-spacing:-0.2px;">Agent Actions</h3>
          <div style="display:flex; flex-direction:column; gap:6px; margin-bottom:14px;">
            <p v-for="a in agentResult.actions" :key="a"
              style="font-size:12.5px; color:var(--gray-600); background:var(--gray-50); border:1px solid var(--gray-100); border-radius:9px; padding:9px 14px; line-height:1.5;">
              {{ a }}
            </p>
          </div>
          <div style="display:flex; gap:8px; flex-wrap:wrap;">
            <span v-if="agentResult.vendor_ticket"
              style="font-size:12px; background:var(--green-light); color:#1a7f3c; padding:6px 14px; border-radius:980px; font-weight:600; border:1px solid rgba(52,199,89,0.2);">
              ✓ Ticket {{ agentResult.vendor_ticket.ticket.ticket_id }}
            </span>
            <span v-if="agentResult.reschedules?.length"
              style="font-size:12px; background:var(--blue-light); color:var(--blue); padding:6px 14px; border-radius:980px; font-weight:600; border:1px solid rgba(0,113,227,0.15);">
              ✓ {{ agentResult.reschedules.length }} appointment(s) rescheduled
            </span>
          </div>
        </div>
      </Transition>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '../composables/useApi'
import RiskBadge      from '../components/RiskBadge.vue'
import StatCard       from '../components/StatCard.vue'
import SensorSparkline from '../components/SensorSparkline.vue'

const route = useRoute()
const { risk: riskApi, telemetry: telApi, sensorChart, agentRun } = useApi()

const machineId    = computed(() => route.params.id)
const isMRI        = computed(() => String(machineId.value).includes('MRI'))
const loading      = ref(true)
const chartLoading = ref(false)
const running      = ref(false)
const risk         = ref(null)
const latest       = ref(null)
const chartData    = ref([])
const agentResult  = ref(null)
const activeSensor = ref('')

const RISK_COLORS = {
  NORMAL: 'var(--green)', MONITOR: 'var(--amber)',
  SCHEDULE_MAINTENANCE: 'var(--red)', CRITICAL: 'var(--purple)',
}
const riskColor = computed(() => RISK_COLORS[risk.value?.risk_code] || 'var(--blue)')
const daysColor = computed(() => {
  const d = risk.value?.days_to_failure
  return d <= 3 ? 'var(--red)' : d <= 14 ? 'var(--amber)' : 'var(--green)'
})
const fmt = v => { if (!v) return '0'; return v >= 100000 ? `${(v / 100000).toFixed(1)}L` : `${(v / 1000).toFixed(0)}K` }
const fmtVal = (v, u) => v != null ? `${typeof v === 'number' ? v.toFixed(1) : v}${u ? ' ' + u : ''}` : '—'

const MRI_SENSORS = [
  { key: 'helium_pressure_psi',             label: 'Helium PSI' },
  { key: 'cryogen_level_percent',           label: 'Cryogen'    },
  { key: 'gradient_coil_performance_score', label: 'Gradient'   },
  { key: 'error_code_freq_7d',              label: 'Errors'     },
  { key: 'vibration_amplitude_mm_s',        label: 'Vibration'  },
]
const CT_SENSORS = [
  { key: 'tube_heat_unit_percent',             label: 'Tube Heat' },
  { key: 'detector_calibration_drift_score',   label: 'Detector'  },
  { key: 'xray_tube_current_ma',               label: 'Tube mA'   },
  { key: 'error_code_freq_7d',                 label: 'Errors'    },
  { key: 'vibration_amplitude_mm_s',           label: 'Vibration' },
]
const sensors = computed(() => isMRI.value ? MRI_SENSORS : CT_SENSORS)

const MRI_FIELDS = [
  { key: 'helium_pressure_psi',             label: 'Helium PSI',    unit: 'PSI',  col: 'var(--blue)'    },
  { key: 'cryogen_level_percent',           label: 'Cryogen',       unit: '%',    col: 'var(--blue)'    },
  { key: 'gradient_coil_performance_score', label: 'Gradient',      unit: '',     col: 'var(--gray-800)'},
  { key: 'error_code_freq_7d',              label: 'Errors 7d',     unit: '',     col: 'var(--amber)'   },
  { key: 'vibration_amplitude_mm_s',        label: 'Vibration',     unit: 'mm/s', col: 'var(--gray-800)'},
  { key: 'scan_volume_per_day',             label: 'Scans/Day',     unit: '',     col: 'var(--green)'   },
  { key: 'uptime_hours_per_day',            label: 'Uptime',        unit: 'hr',   col: 'var(--green)'   },
  { key: 'machine_age_years',               label: 'Age',           unit: 'yr',   col: 'var(--gray-600)'},
]
const CT_FIELDS = [
  { key: 'tube_heat_unit_percent',           label: 'Tube Heat',    unit: '%',    col: 'var(--red)'     },
  { key: 'detector_calibration_drift_score', label: 'Detector',     unit: '',     col: 'var(--blue)'    },
  { key: 'xray_tube_current_ma',             label: 'Tube mA',      unit: 'mA',   col: 'var(--gray-800)'},
  { key: 'xray_tube_voltage_kv',             label: 'Tube kV',      unit: 'kV',   col: 'var(--gray-800)'},
  { key: 'error_code_freq_7d',               label: 'Errors 7d',    unit: '',     col: 'var(--amber)'   },
  { key: 'scan_volume_per_day',              label: 'Scans/Day',    unit: '',     col: 'var(--green)'   },
  { key: 'uptime_hours_per_day',             label: 'Uptime',       unit: 'hr',   col: 'var(--green)'   },
  { key: 'machine_age_years',                label: 'Age',          unit: 'yr',   col: 'var(--gray-600)'},
]
const telemetryFields = computed(() => isMRI.value ? MRI_FIELDS : CT_FIELDS)

const selectSensor = async key => {
  activeSensor.value = key
  chartLoading.value = true
  try { const { data } = await sensorChart(machineId.value, key); chartData.value = data.data } catch {}
  chartLoading.value = false
}
const load = async () => {
  loading.value = true
  try {
    const [rRes, tRes] = await Promise.all([riskApi(machineId.value), telApi(machineId.value)])
    risk.value = rRes.data
    const recs = tRes.data.records
    latest.value = recs[recs.length - 1]
    activeSensor.value = sensors.value[0].key
    await selectSensor(activeSensor.value)
  } catch (e) { console.error(e) }
  loading.value = false
}
const runAgent = async () => {
  running.value = true
  try { const { data } = await agentRun(machineId.value); agentResult.value = data } catch (e) { console.error(e) }
  running.value = false
}
watch(machineId, () => { agentResult.value = null; load() })
onMounted(load)
</script>
