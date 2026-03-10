<template>
  <div style="padding:32px 28px; min-height:100vh; background:var(--white);">

    <div class="fade-up" style="margin-bottom:32px;">
      <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:16px;">
        <div>
          <p style="font-size:12px; text-transform:uppercase; letter-spacing:0.1em; color:var(--blue); font-weight:700; margin-bottom:6px;"></p>
          <h1 style="font-size:28px; font-weight:800; color:var(--gray-900); letter-spacing:-0.6px; line-height:1.15;">Equipment Dashboard</h1>
          <p style="font-size:14px; color:var(--gray-400); margin-top:6px; font-weight:400;">Predictive Maintenance Intelligence · Real-time telemetry</p>
        </div>
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
          <span style="font-size:11px; color:var(--gray-500); background:var(--gray-100); padding:7px 14px; border-radius:980px; font-weight:600; border:1px solid var(--gray-200);">
            {{ time }}
          </span>
          <button @click="refresh" :disabled="loading" class="btn-secondary" style="font-size:12px; gap:6px;">
            <div v-if="loading" class="spinner" style="width:12px; height:12px; border-width:1.5px;"></div>
            <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M3 12a9 9 0 009 9 9.75 9.75 0 006.74-2.74L21 21"/>
              <path d="M21 3v6h-6"/>
              <path d="M21 12a9 9 0 00-9-9 9.75 9.75 0 00-6.74 2.74L3 3"/>
            </svg>
            Refresh
          </button>
          <button @click="runAll" :disabled="running" class="btn-primary" style="font-size:12px;">
            <div v-if="running" class="spinner" style="width:12px; height:12px; border-width:1.5px; border-top-color:white; border-color:rgba(255,255,255,0.3);"></div>
            {{ running ? 'Running Agent…' : '⚡ Run All Agents' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading && !machines.length" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:300px; gap:14px;">
      <div class="spinner" style="width:28px; height:28px; border-width:2.5px;"></div>
      <p style="font-size:13px; color:var(--gray-400); font-weight:500;">Loading telemetry data…</p>
    </div>

    <template v-else>
      <div v-if="criticals.length" class="fade-up" style="margin-bottom:20px; padding:14px 20px; background:var(--purple-light); border:1px solid rgba(175,82,222,0.2); border-radius:var(--radius-md); display:flex; align-items:center; gap:12px;">
        <span style="width:32px; height:32px; border-radius:50%; background:white; display:flex; align-items:center; justify-content:center; flex-shrink:0; box-shadow:var(--shadow-sm);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#af52de" stroke-width="2.5">
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </span>
        <div>
          <p style="font-size:13px; font-weight:700; color:#7b2fa8;">Critical Alert — Immediate Action Required</p>
          <p style="font-size:12px; color:#9b45c4; margin-top:2px;">
            {{ criticals.map(m => m.machine_id).join(', ') }} — Failure imminent. Suspend use and contact vendor.
          </p>
        </div>
      </div>

      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(360px,1fr)); gap:16px; margin-bottom:20px;">
        <div v-for="(m, i) in machines" :key="m.machine_id" class="fade-up" :class="`fade-up-${i + 1}`">
          <MachineCard :machine="m" @run="onRun" />
        </div>
      </div>

      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(340px,1fr)); gap:16px; margin-bottom:20px;">
        <div class="fade-up fade-up-3"><CostPanel :machines="machines" /></div>
        <div class="fade-up fade-up-4"><AnomalyHeatmap :machines="machines" /></div>
      </div>

      <Transition name="slide">
        <div v-if="agentResult" class="card fade-in" style="padding:24px;">
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:16px;">
            <div style="display:flex; align-items:center; gap:10px;">
              <div style="width:32px; height:32px; border-radius:9px; background:var(--blue-light); display:flex; align-items:center; justify-content:center;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" stroke-width="2">
                  <polygon points="5,3 19,12 5,21"/>
                </svg>
              </div>
              <h3 style="font-size:15px; font-weight:700; color:var(--gray-900);">Agent Run Complete</h3>
            </div>
            <button @click="agentResult = null"
              style="width:28px; height:28px; border-radius:50%; background:var(--gray-100); border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; color:var(--gray-500); font-size:14px; transition:background 0.15s;"
              @mouseenter="e => e.target.style.background='var(--gray-200)'"
              @mouseleave="e => e.target.style.background='var(--gray-100)'">✕</button>
          </div>
          <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:12px;">
            <div v-for="(res, mid) in (agentResult.results || {})" :key="mid"
              style="background:var(--gray-50); border:1px solid var(--gray-100); border-radius:var(--radius-md); padding:14px;">
              <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
                <span style="font-size:13px; font-weight:700; color:var(--gray-900);">{{ mid }}</span>
                <RiskBadge :code="res.risk?.risk_code" />
              </div>
              <div style="display:flex; flex-direction:column; gap:4px;">
                <p v-for="a in res.actions" :key="a" style="font-size:12px; color:var(--gray-600); line-height:1.6;">{{ a }}</p>
              </div>
              <div style="display:flex; gap:6px; margin-top:10px; flex-wrap:wrap;">
                <span v-if="res.vendor_ticket" style="font-size:11px; background:var(--green-light); color:#1a7f3c; padding:3px 10px; border-radius:980px; font-weight:600; border:1px solid rgba(52,199,89,0.2);">✓ Ticket raised</span>
                <span v-if="res.reschedules?.length" style="font-size:11px; background:var(--blue-light); color:var(--blue); padding:3px 10px; border-radius:980px; font-weight:600; border:1px solid rgba(0,113,227,0.15);">✓ {{ res.reschedules.length }} rescheduled</span>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useApi } from '../composables/useApi'
import MachineCard   from '../components/MachineCard.vue'
import CostPanel     from '../components/CostPanel.vue'
import AnomalyHeatmap from '../components/AnomalyHeatmap.vue'
import RiskBadge     from '../components/RiskBadge.vue'

const { dashboard, agentRunAll } = useApi()
const machines    = ref([])
const loading     = ref(true)
const running     = ref(false)
const agentResult = ref(null)
const time        = ref('')

const criticals = computed(() => machines.value.filter(m => m.risk.risk_tier >= 3))
let tid
const tick = () => {
  time.value = new Date().toLocaleString('en-IN', {
    weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}
const refresh = async () => {
  loading.value = true
  try { const { data } = await dashboard(); machines.value = data.machines } catch (e) { console.error(e) }
  loading.value = false
}
const runAll = async () => {
  running.value = true
  try { const { data } = await agentRunAll(); agentResult.value = data } catch (e) { console.error(e) }
  running.value = false
}
const onRun = res => { agentResult.value = { results: { [res.machine_id]: res } } }
onMounted(() => { refresh(); tick(); tid = setInterval(tick, 60000) })
onUnmounted(() => clearInterval(tid))
</script>
