<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H}`" style="width:100%; height:120px;" preserveAspectRatio="none">
      <defs>
        <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stop-color="#0071e3" stop-opacity="0.18"/>
          <stop offset="100%" stop-color="#0071e3" stop-opacity="0"/>
        </linearGradient>
        <linearGradient id="sg2" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%"   stop-color="#0071e3" stop-opacity="0"/>
          <stop offset="20%"  stop-color="#0071e3" stop-opacity="1"/>
          <stop offset="80%"  stop-color="#0071e3" stop-opacity="1"/>
          <stop offset="100%" stop-color="#0071e3" stop-opacity="0"/>
        </linearGradient>
      </defs>

      <path v-if="bandPath" :d="bandPath"
        fill="rgba(0,113,227,0.04)" stroke="rgba(0,113,227,0.08)" stroke-width="0.5"/>

      <line v-if="vals.length"
        :x1="0" :y1="yv(mean)" :x2="W" :y2="yv(mean)"
        stroke="rgba(0,113,227,0.2)" stroke-width="1" stroke-dasharray="4 4"/>

      <path v-if="areaPath" :d="areaPath" fill="url(#sg)"/>

      <path v-if="linePath" :d="linePath" fill="none"
        stroke="url(#sg2)" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"
        style="filter:drop-shadow(0 2px 6px rgba(0,113,227,0.25))"/>

      <g v-for="(pt, i) in anomDots" :key="i">
        <circle :cx="pt.x" :cy="pt.y" r="6" fill="rgba(255,59,48,0.12)"/>
        <circle :cx="pt.x" :cy="pt.y" r="3" fill="#ff3b30"/>
      </g>

      <g v-if="lastPt">
        <circle :cx="lastPt.x" :cy="lastPt.y" r="5" fill="rgba(0,113,227,0.15)"/>
        <circle :cx="lastPt.x" :cy="lastPt.y" r="3" fill="#0071e3"/>
      </g>
    </svg>

    <div style="display:flex; justify-content:space-between; margin-top:4px;">
      <span style="font-size:10px; color:var(--gray-400); font-weight:500;">{{ data[0]?.date }}</span>
      <span style="font-size:10px; color:var(--gray-400); font-weight:500;">{{ data[data.length - 1]?.date }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const p = defineProps({ data: { type: Array, default: () => [] } })
const W = 600; const H = 110; const PAD = 12

const vals  = computed(() => p.data.map(d => d.value).filter(v => v != null))
const minV  = computed(() => vals.value.length ? Math.min(...vals.value) * 0.97 : 0)
const maxV  = computed(() => vals.value.length ? Math.max(...vals.value) * 1.03 : 1)
const mean  = computed(() => p.data[0]?.mean ?? 0)
const upper = computed(() => p.data[0]?.upper ?? 0)
const lower = computed(() => p.data[0]?.lower ?? 0)

const yv = v => {
  const r = maxV.value - minV.value
  return r === 0 ? H / 2 : H - PAD - ((v - minV.value) / r) * (H - 2 * PAD)
}
const xi = i => (i / Math.max(p.data.length - 1, 1)) * W

const linePath = computed(() =>
  p.data.map((d, i) => d.value != null ? `${i === 0 ? 'M' : 'L'}${xi(i).toFixed(1)},${yv(d.value).toFixed(1)}` : '').filter(Boolean).join(' ')
)
const areaPath = computed(() => {
  if (!p.data.length) return ''
  const pts = p.data.map((d, i) => d.value != null ? `${xi(i).toFixed(1)},${yv(d.value).toFixed(1)}` : null).filter(Boolean)
  return `M${xi(0)},${H} L${pts.join(' L')} L${xi(p.data.length - 1)},${H} Z`
})
const bandPath = computed(() => {
  if (!p.data.length) return ''
  const top = p.data.map((_, i) => `${xi(i).toFixed(1)},${yv(upper.value).toFixed(1)}`).join(' L')
  const bot = [...p.data].reverse().map((_, i) => `${xi(p.data.length - 1 - i).toFixed(1)},${yv(lower.value).toFixed(1)}`).join(' L')
  return `M${top} L${bot} Z`
})
const anomDots = computed(() =>
  p.data.map((d, i) => (d.value != null && (d.value > d.upper || d.value < d.lower)) ? { x: xi(i), y: yv(d.value) } : null).filter(Boolean)
)
const lastPt = computed(() => {
  const last = [...p.data].reverse().find(d => d.value != null)
  if (!last) return null
  const i = p.data.lastIndexOf(last)
  return { x: xi(i), y: yv(last.value) }
})
</script>
