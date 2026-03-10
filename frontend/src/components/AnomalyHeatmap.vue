<template>
  <div class="card" style="padding:22px;">
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; flex-wrap:wrap; gap:8px;">
      <div style="display:flex; align-items:center; gap:8px;">
        <div style="width:30px; height:30px; border-radius:8px; background:var(--blue-light); display:flex; align-items:center; justify-content:center;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" stroke-width="2">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
        </div>
        <h3 style="font-size:15px; font-weight:700; color:var(--gray-900); letter-spacing:-0.2px;">Anomaly Timeline</h3>
      </div>

      <div style="display:flex; gap:4px; background:var(--gray-100); border-radius:8px; padding:3px;">
        <button v-for="id in ['MRI_01', 'CT_01']" :key="id" @click="selected = id"
          style="padding:5px 14px; border-radius:6px; font-size:12px; cursor:pointer; transition:all 0.2s var(--ease-out); border:none; font-weight:600; font-family:'Manrope',sans-serif;"
          :style="selected === id
            ? 'background:white; color:var(--gray-900); box-shadow:var(--shadow-sm);'
            : 'background:transparent; color:var(--gray-500);'">
          {{ id }}
        </button>
      </div>
    </div>

    <div v-if="loading" style="height:120px; display:flex; align-items:center; justify-content:center;">
      <div class="spinner"></div>
    </div>

    <div v-else>
      <p style="font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700; margin-bottom:8px;">Z-Score Anomalies per Day</p>
      <div style="display:flex; gap:3px; flex-wrap:wrap; margin-bottom:16px;">
        <div v-for="(d, i) in chartData" :key="i"
          style="position:relative; width:20px; height:20px; border-radius:5px; cursor:pointer; transition:transform 0.15s;"
          :style="{ background: heatColor(d.anomaly_count) }"
          :title="`${d.date}: ${d.anomaly_count} anomalies`"
          @mouseenter="hov = i" @mouseleave="hov = -1">
          <div v-if="hov === i"
            style="position:absolute; bottom:calc(100% + 6px); left:50%; transform:translateX(-50%); background:var(--gray-900); color:white; padding:4px 8px; border-radius:6px; font-size:10px; white-space:nowrap; z-index:20; pointer-events:none; font-weight:600; box-shadow:var(--shadow-md);">
            {{ d.date }}: {{ d.anomaly_count }}
          </div>
        </div>
      </div>

      <p style="font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700; margin-bottom:6px;">Isolation Forest</p>
      <div style="display:flex; gap:3px; margin-bottom:16px;">
        <div v-for="(d, i) in chartData" :key="`iso${i}`"
          style="width:20px; height:8px; border-radius:3px; transition:all 0.2s;"
          :style="{ background: d.iso_anomaly ? 'var(--red)' : 'var(--gray-100)' }">
        </div>
      </div>

      <div v-if="latestFlags.length" style="border-top:1px solid var(--gray-100); padding-top:14px;">
        <p style="font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700; margin-bottom:8px;">Latest Flags</p>
        <div style="display:flex; flex-direction:column; gap:5px; max-height:130px; overflow-y:auto;">
          <div v-for="f in latestFlags" :key="f.parameter"
            style="display:flex; align-items:center; justify-content:space-between; padding:7px 12px; border-radius:9px; background:var(--gray-50); border:1px solid var(--gray-100);">
            <span style="font-size:12px; color:var(--gray-700); font-weight:500;">{{ f.parameter.replace(/_/g, ' ') }}</span>
            <div style="display:flex; align-items:center; gap:6px;">
              <span style="font-size:11px; font-weight:600;"
                :style="f.direction === 'HIGH' ? 'color:var(--red)' : 'color:var(--blue)'">
                {{ f.direction }}
              </span>
              <span style="font-size:10px; padding:2px 8px; border-radius:980px; font-weight:600;"
                :style="f.severity === 'CRITICAL'
                  ? 'background:var(--red-light); color:#c0392b;'
                  : 'background:var(--amber-light); color:#b86e00;'">
                {{ f.severity }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div style="display:flex; align-items:center; gap:8px; margin-top:14px; font-size:11px; color:var(--gray-400); font-weight:500;">
        <span>None</span>
        <div style="display:flex; gap:3px;">
          <div v-for="n in 5" :key="n" style="width:14px; height:14px; border-radius:3px;" :style="{ background: heatColor((n - 1) * 2) }"></div>
        </div>
        <span>High</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useApi } from '../composables/useApi'

const { anomalies } = useApi()
const selected  = ref('MRI_01')
const loading   = ref(false)
const cache     = ref({})
const hov       = ref(-1)

const chartData    = computed(() => cache.value[selected.value]?.chart_data || [])
const latestFlags  = computed(() => {
  const cd = chartData.value
  return cd.length ? (cd[cd.length - 1].flags || []) : []
})

const heatColor = n => {
  if (n === 0) return 'var(--gray-100)'
  if (n === 1) return 'rgba(255,159,10,0.25)'
  if (n <= 3)  return 'rgba(255,59,48,0.3)'
  return 'var(--red)'
}

const fetchData = async id => {
  if (cache.value[id]) return
  loading.value = true
  try {
    const { data } = await anomalies(id)
    cache.value[id] = data
  } catch {}
  loading.value = false
}

watch(selected, fetchData)
onMounted(() => fetchData(selected.value))
</script>
