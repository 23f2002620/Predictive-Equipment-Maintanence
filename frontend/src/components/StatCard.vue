<template>
  <div class="stat-surface" style="padding:14px 16px;">
    <p style="font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-500); font-weight:700; margin-bottom:6px;">{{ label }}</p>
    <p style="font-size:22px; font-weight:800; line-height:1; letter-spacing:-0.5px;" :style="{ color: color || 'var(--gray-900)' }">{{ value }}</p>
    <p v-if="sub" style="font-size:11px; color:var(--gray-400); margin-top:5px; font-weight:500;">{{ sub }}</p>
  </div>
</template>

<script setup>
defineProps({ label: String, value: String, color: String, sub: String })
</script>
