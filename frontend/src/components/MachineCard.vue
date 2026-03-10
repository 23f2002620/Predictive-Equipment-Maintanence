<template>
  <div class="card card-lift" style="padding:24px; cursor:default;"
    @mouseenter="hovered=true" @mouseleave="hovered=false">

    <div style="display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:20px;">
      <div style="display:flex; align-items:center; gap:14px;">
        <div style="width:48px; height:48px; border-radius:14px; display:flex; align-items:center; justify-content:center; transition:all 0.3s var(--ease-out);"
          :style="{background: hovered ? '#f0f7ff' : 'var(--gray-100)', boxShadow: hovered ? '0 0 0 4px rgba(0,113,227,0.08)' : 'none'}">
          <svg v-if="isMRI" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0071e3" stroke-width="1.8">
            <circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/>
          </svg>
          <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0071e3" stroke-width="1.8">
            <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/>
            <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
          </svg>
        </div>
        <div>
          <div style="display:flex; align-items:center; gap:8px;">
            <h3 style="font-size:17px; font-weight:800; color:var(--gray-900); letter-spacing:-0.3px;">{{ m.machine_id }}</h3>
            <span style="font-size:10px; padding:2px 8px; border-radius:5px; background:var(--gray-100); color:var(--gray-500); font-weight:700; letter-spacing:0.05em;">{{ m.machine_type }}</span>
          </div>
          <p style="font-size:12px; color:var(--gray-400); margin-top:2px; font-weight:500;">{{ m.manufacturer }} · {{ m.model }}</p>
        </div>
      </div>
      <RiskBadge :code="m.risk.risk_code" />
    </div>

    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:16px;">
      <StatCard label="Days to Failure" :value="m.risk.days_to_failure>=999?'∞':`${m.risk.days_to_failure}d`" :color="daysColor" />
      <StatCard label="Confidence"      :value="`${(m.risk.confidence*100).toFixed(0)}%`" color="var(--blue)" />
      <StatCard label="Anomalies"       :value="String(m.risk.anomaly_count_last7d)" :color="m.risk.anomaly_count_last7d>3?'var(--red)':'var(--amber)'" sub="last 7 days" />
    </div>

    <div style="background:var(--gray-50); border:1px solid var(--gray-200); border-radius:var(--radius-md); padding:12px 14px; margin-bottom:14px;">
      <p style="font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700; margin-bottom:5px;">Predicted Failure</p>
      <p style="font-size:13px; color:var(--gray-700); font-weight:500; line-height:1.5;">{{ m.risk.failure_description }}</p>
    </div>

    <div v-if="m.risk.flagged_parameters?.length" style="margin-bottom:14px;">
      <p style="font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700; margin-bottom:7px;">Flagged Sensors</p>
      <div style="display:flex; flex-wrap:wrap; gap:5px;">
        <span v-for="f in m.risk.flagged_parameters.slice(0,5)" :key="f.parameter"
          style="padding:3px 10px; font-size:11px; border-radius:980px; font-weight:600;"
          :style="f.severity==='CRITICAL'?'background:var(--red-light);color:#c0392b;border:1px solid rgba(255,59,48,0.15);':'background:var(--amber-light);color:#b86e00;border:1px solid rgba(255,159,10,0.15);'">
          {{ f.parameter.replace(/_/g,' ') }}
        </span>
      </div>
    </div>

    <div v-if="m.risk.cost_impact" style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:18px;">
      <div style="background:var(--green-light); border-radius:var(--radius-sm); padding:10px 12px; border:1px solid rgba(52,199,89,0.15);">
        <p style="font-size:10px; color:#1a7f3c; font-weight:600; margin-bottom:3px;">Preventive</p>
        <p style="font-size:16px; font-weight:800; color:#1a7f3c; letter-spacing:-0.3px;">₹{{ fmt(m.risk.cost_impact.preventive_cost_inr) }}</p>
      </div>
      <div style="background:var(--red-light); border-radius:var(--radius-sm); padding:10px 12px; border:1px solid rgba(255,59,48,0.15);">
        <p style="font-size:10px; color:#c0392b; font-weight:600; margin-bottom:3px;">Breakdown</p>
        <p style="font-size:16px; font-weight:800; color:#c0392b; letter-spacing:-0.3px;">₹{{ fmt(m.risk.cost_impact.total_breakdown_cost_inr) }}</p>
      </div>
    </div>

    <div style="display:flex; gap:8px;">
      <RouterLink :to="`/machine/${m.machine_id}`" class="btn-secondary" style="flex:1; font-size:12px;">Details</RouterLink>
      <button @click="runAgent" :disabled="running" class="btn-primary" style="flex:1; font-size:12px;">
        <div v-if="running" class="spinner" style="width:13px; height:13px; border-width:1.5px;"></div>
        {{ running ? 'Running…' : 'Run Agent' }}
      </button>
    </div>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useApi } from '../composables/useApi'
import RiskBadge from './RiskBadge.vue'
import StatCard from './StatCard.vue'

const props = defineProps({ machine: Object })
const emit  = defineEmits(['run'])
const m = computed(() => props.machine)
const hovered = ref(false)
const running = ref(false)
const isMRI = computed(() => m.value.machine_type === 'MRI')
const daysColor = computed(() => {
  const d = m.value.risk.days_to_failure
  return d <= 3 ? 'var(--red)' : d <= 14 ? 'var(--amber)' : 'var(--green)'
})
const fmt = v => { if(!v)return'0'; return v>=100000?`${(v/100000).toFixed(1)}L`:`${(v/1000).toFixed(0)}K` }
const runAgent = async () => {
  running.value = true
  try { const { data } = await useApi().agentRun(m.value.machine_id); emit('run', data) } catch(e) { console.error(e) }
  running.value = false
}
</script>