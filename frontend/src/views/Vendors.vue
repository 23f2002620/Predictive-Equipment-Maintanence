<template>
  <div style="padding:32px 28px; background:var(--white); min-height:100vh;">
    <div class="fade-up" style="margin-bottom:28px;">
      <p style="font-size:12px; text-transform:uppercase; letter-spacing:0.1em; color:var(--blue); font-weight:700; margin-bottom:6px;">Operations</p>
      <h1 style="font-size:28px; font-weight:800; color:var(--gray-900); letter-spacing:-0.6px;">Service Vendors</h1>
      <p style="font-size:14px; color:var(--gray-400); margin-top:6px;">Authorized equipment service partners</p>
    </div>

    <div v-if="loading" style="display:flex; align-items:center; justify-content:center; height:200px;">
      <div class="spinner" style="width:24px; height:24px;"></div>
    </div>

    <div v-else style="display:grid; grid-template-columns:repeat(auto-fill, minmax(360px,1fr)); gap:16px;">
      <div v-for="v in vendors" :key="v.vendor_id" class="card card-lift" style="padding:24px;">

        <div style="display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:16px;">
          <div style="display:flex; align-items:center; gap:14px;">
            <div style="width:46px; height:46px; border-radius:13px; background:var(--blue-light); display:flex; align-items:center; justify-content:center; flex-shrink:0;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" stroke-width="1.8">
                <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0H3m2 0H3m12-13h-4m4 4h-4m4 4h-4M9 7H7m2 4H7m2 4H7"/>
              </svg>
            </div>
            <div>
              <h3 style="font-size:16px; font-weight:800; color:var(--gray-900); letter-spacing:-0.3px; line-height:1.1;">{{ v.vendor_name }}</h3>
              <p style="font-size:12px; color:var(--gray-400); margin-top:2px; font-weight:500;">{{ v.specialization }}</p>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:4px; background:var(--amber-light); padding:5px 10px; border-radius:980px; border:1px solid rgba(255,159,10,0.2); flex-shrink:0;">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="#ff9f0a" stroke="none">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 21 12 17.77 5.82 21 7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            <span style="font-size:12px; font-weight:800; color:#b86e00;">{{ v.service_rating }}</span>
          </div>
        </div>

        <div class="divider" style="margin:0 0 16px;"></div>

        <div style="display:flex; flex-direction:column; gap:9px; margin-bottom:18px;">
          <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:28px; height:28px; border-radius:8px; background:var(--gray-100); display:flex; align-items:center; justify-content:center; flex-shrink:0;">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--gray-500)" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <span style="font-size:13px; color:var(--gray-700); font-weight:500;">{{ v.contact_person }}</span>
          </div>
          <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:28px; height:28px; border-radius:8px; background:var(--gray-100); display:flex; align-items:center; justify-content:center; flex-shrink:0;">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--gray-500)" stroke-width="2"><path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
            </div>
            <span style="font-size:13px; color:var(--gray-700); font-weight:500; font-variant-numeric:tabular-nums;">{{ v.phone }}</span>
          </div>
          <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:28px; height:28px; border-radius:8px; background:var(--gray-100); display:flex; align-items:center; justify-content:center; flex-shrink:0;">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--gray-500)" stroke-width="2"><path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
            </div>
            <span style="font-size:13px; color:var(--blue); font-weight:500;">{{ v.email }}</span>
          </div>
        </div>

        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-bottom:14px;">
          <div class="stat-surface" style="padding:12px; text-align:center;">
            <p style="font-size:10px; color:var(--gray-400); font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Response</p>
            <p style="font-size:18px; font-weight:800; color:var(--blue); letter-spacing:-0.3px;">{{ v.response_time_hours }}<span style="font-size:11px; font-weight:600; color:var(--gray-400); margin-left:1px;">hr</span></p>
          </div>
          <div class="stat-surface" style="padding:12px; text-align:center;">
            <p style="font-size:10px; color:var(--gray-400); font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Hourly</p>
            <p style="font-size:18px; font-weight:800; color:var(--gray-800); letter-spacing:-0.3px;">₹{{ (v.hourly_rate_inr / 1000).toFixed(1) }}<span style="font-size:11px; font-weight:600; color:var(--gray-400); margin-left:1px;">K</span></p>
          </div>
          <div class="stat-surface" style="padding:12px; text-align:center;">
            <p style="font-size:10px; color:var(--gray-400); font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Rating</p>
            <p style="font-size:18px; font-weight:800; color:#b86e00; letter-spacing:-0.3px;">{{ v.service_rating }}<span style="font-size:11px; font-weight:600; color:var(--gray-400); margin-left:1px;">/5</span></p>
          </div>
        </div>

        <div style="background:var(--gray-50); border:1px solid var(--gray-100); border-radius:9px; padding:10px 14px;">
          <span style="font-size:11px; color:var(--gray-400); font-weight:700; text-transform:uppercase; letter-spacing:0.05em;">Availability · </span>
          <span style="font-size:12px; color:var(--gray-700); font-weight:500;">{{ v.available_slots }}</span>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
const { vendors: vendorsApi } = useApi()
const vendors = ref([])
const loading = ref(true)
onMounted(async () => {
  try { const { data } = await vendorsApi(); vendors.value = data.vendors || [] } catch (e) { console.error(e) }
  loading.value = false
})
</script>
