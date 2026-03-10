<template>
  <span
    style="display:inline-flex; align-items:center; gap:5px; padding:4px 12px; border-radius:980px; font-size:11.5px; font-weight:600; letter-spacing:0.01em;"
    :class="info.cls"
  >
    <span style="width:5px; height:5px; border-radius:50%; background:currentColor; opacity:0.7;"></span>
    {{ info.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
const p = defineProps({ code: String })
const MAP = {
  NORMAL:               { label: 'Normal',               cls: 'risk-normal'   },
  MONITOR:              { label: 'Monitor',              cls: 'risk-monitor'  },
  SCHEDULE_MAINTENANCE: { label: 'Schedule Maintenance', cls: 'risk-schedule' },
  CRITICAL:             { label: 'Critical',             cls: 'risk-critical' },
}
const info = computed(() => MAP[p.code] || MAP.NORMAL)
</script>
