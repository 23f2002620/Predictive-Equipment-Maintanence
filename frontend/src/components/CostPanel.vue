<template>
  <div class="card" style="padding:22px;">
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:18px;">
      <div style="width:30px; height:30px; border-radius:8px; background:var(--green-light); display:flex; align-items:center; justify-content:center;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#1a7f3c" stroke-width="2">
          <path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
        </svg>
      </div>
      <h3 style="font-size:15px; font-weight:700; color:var(--gray-900); letter-spacing:-0.2px;">Cost Impact</h3>
    </div>

    <div style="display:flex; flex-direction:column; gap:22px;">
      <div v-for="m in machines" :key="m.machine_id">

        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:13px; font-weight:700; color:var(--gray-800);">{{ m.machine_id }}</span>
            <RiskBadge :code="m.risk.risk_code" />
          </div>
          <div>
            <p style="font-size:10px; color:var(--gray-400); text-align:right; font-weight:600;">NET SAVING</p>
            <p style="font-size:16px; font-weight:800; color:var(--green); letter-spacing:-0.3px;">
              ₹{{ fmt(m.risk.cost_impact?.net_saving_inr) }}
            </p>
          </div>
        </div>

        <div v-if="m.risk.cost_impact" style="margin-bottom:10px;">
          <div style="display:flex; justify-content:space-between; font-size:11px; color:var(--gray-500); margin-bottom:4px; font-weight:600;">
            <span>Preventive</span>
            <span>₹{{ fmt(m.risk.cost_impact.preventive_cost_inr) }}</span>
          </div>
          <div style="height:7px; background:var(--gray-100); border-radius:4px; overflow:hidden; margin-bottom:8px;">
            <div style="height:100%; border-radius:4px; background:linear-gradient(90deg,#34c759,#30d158); transition:width 1s var(--ease-out);"
              :style="{ width: pct(m) + '%' }"></div>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:11px; color:var(--gray-400); margin-bottom:4px; font-weight:600;">
            <span>Breakdown</span>
            <span>₹{{ fmt(m.risk.cost_impact.total_breakdown_cost_inr) }}</span>
          </div>
          <div style="height:7px; background:var(--red-light); border-radius:4px;"></div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
          <div v-for="item in items(m)" :key="item.l"
            style="background:var(--gray-50); border:1px solid var(--gray-100); border-radius:9px; padding:8px 11px;">
            <p style="font-size:10px; color:var(--gray-400); font-weight:600;">{{ item.l }}</p>
            <p style="font-size:13px; color:var(--gray-800); font-weight:700; margin-top:2px;">{{ item.v }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import RiskBadge from './RiskBadge.vue'
defineProps({ machines: Array })

const fmt = v => {
  if (!v) return '0'
  return v >= 100000 ? `${(v / 100000).toFixed(1)}L` : `${(v / 1000).toFixed(0)}K`
}
const pct = m => {
  const p = m.risk.cost_impact?.preventive_cost_inr || 1
  const b = m.risk.cost_impact?.total_breakdown_cost_inr || 1
  return Math.round((p / b) * 100)
}
const items = m => [
  { l: 'Emergency Repair', v: `₹${fmt(m.risk.cost_impact?.emergency_repair_cost_inr)}` },
  { l: 'Revenue/Day Lost', v: `₹${fmt(m.risk.cost_impact?.lost_revenue_per_day_inr)}`  },
  { l: 'Downtime',         v: `${m.risk.cost_impact?.downtime_days || 0} days`          },
  { l: 'Net Saving',       v: `₹${fmt(m.risk.cost_impact?.net_saving_inr)}`             },
]
</script>
