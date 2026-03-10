<template>
  <div style="padding:32px 28px; background:var(--white); min-height:100vh;">
    <div class="fade-up" style="margin-bottom:28px;">
      <p style="font-size:12px; text-transform:uppercase; letter-spacing:0.1em; color:var(--blue); font-weight:700; margin-bottom:6px;">Operations</p>
      <h1 style="font-size:28px; font-weight:800; color:var(--gray-900); letter-spacing:-0.6px;">Patient Schedule</h1>
      <p style="font-size:14px; color:var(--gray-400); margin-top:6px;">Upcoming scan appointments · Next 7 days</p>
    </div>

    <div v-if="loading" style="display:flex; align-items:center; justify-content:center; height:200px;">
      <div class="spinner" style="width:24px; height:24px;"></div>
    </div>

    <template v-else>
      <div class="fade-up fade-up-1" style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:20px;">
        <StatCard label="Total Appointments" :value="String(allAppointments.length)"   color="var(--blue)"   />
        <StatCard label="MRI Appointments"   :value="String(mriCount)"                 color="var(--blue)"   />
        <StatCard label="CT Appointments"    :value="String(ctCount)"                  color="var(--purple)" />
        <StatCard label="Rescheduled"        :value="String(rescheduledCount)"          color="var(--amber)"  />
      </div>

      <div class="card fade-up fade-up-2">
        <div style="padding:16px 20px; border-bottom:1px solid var(--gray-100); display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
          <h3 style="font-size:15px; font-weight:700; color:var(--gray-900); letter-spacing:-0.2px;">All Appointments</h3>
          <!-- Segmented filter -->
          <div style="display:flex; gap:4px; background:var(--gray-100); border-radius:8px; padding:3px;">
            <button v-for="f in filters" :key="f" @click="activeFilter = f"
              style="padding:5px 14px; border-radius:6px; font-size:12px; cursor:pointer; transition:all 0.2s var(--ease-out); border:none; font-weight:600; font-family:'Manrope',sans-serif;"
              :style="activeFilter === f
                ? 'background:white; color:var(--gray-900); box-shadow:var(--shadow-sm);'
                : 'background:transparent; color:var(--gray-500);'">
              {{ f }}
            </button>
          </div>
        </div>

        <div style="overflow-x:auto;">
          <table style="width:100%; border-collapse:collapse; font-size:13px;">
            <thead>
              <tr style="border-bottom:1px solid var(--gray-100);">
                <th v-for="h in headers" :key="h"
                  style="padding:12px 18px; text-align:left; font-size:10px; color:var(--gray-400); text-transform:uppercase; letter-spacing:0.08em; font-weight:700; background:var(--gray-50);">
                  {{ h }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appt in filtered" :key="appt.appointment_id"
                style="border-bottom:1px solid var(--gray-50); transition:background 0.15s; cursor:default;"
                @mouseenter="e => e.currentTarget.style.background = 'var(--gray-50)'"
                @mouseleave="e => e.currentTarget.style.background = 'transparent'">
                <td style="padding:13px 18px; font-weight:700; color:var(--blue); font-size:12px;">{{ appt.appointment_id }}</td>
                <td style="padding:13px 18px;">
                  <span style="padding:3px 10px; border-radius:980px; font-size:11px; font-weight:700;"
                    :style="appt.machine_id === 'MRI_01'
                      ? 'background:var(--blue-light); color:var(--blue);'
                      : 'background:var(--purple-light); color:var(--purple);'">
                    {{ appt.machine_id }}
                  </span>
                </td>
                <td style="padding:13px 18px; color:var(--gray-500); font-size:12px;">{{ appt.patient_id }}</td>
                <td style="padding:13px 18px; color:var(--gray-700); font-weight:600;">{{ appt.scan_date }}</td>
                <td style="padding:13px 18px; color:var(--gray-500);">{{ appt.scan_time }}</td>
                <td style="padding:13px 18px;">
                  <span style="padding:3px 10px; border-radius:980px; font-size:11px; font-weight:600;"
                    :style="appt.patient_priority === 'emergency'
                      ? 'background:var(--red-light); color:#c0392b;'
                      : appt.patient_priority === 'urgent'
                        ? 'background:var(--amber-light); color:#b86e00;'
                        : 'background:var(--gray-100); color:var(--gray-500);'">
                    {{ appt.patient_priority }}
                  </span>
                </td>
                <td style="padding:13px 18px; color:var(--gray-500);">{{ appt.scan_duration_min }} min</td>
                <td style="padding:13px 18px;">
                  <span v-if="appt.rescheduled" style="color:var(--amber); font-size:12px; font-weight:600;">
                    ↪ {{ appt.new_appointment_slot }}
                  </span>
                  <span v-else style="color:var(--green); font-size:12px; font-weight:600;">✓ Confirmed</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import StatCard from '../components/StatCard.vue'

const { schedule } = useApi()
const loading         = ref(true)
const allAppointments = ref([])
const activeFilter    = ref('All')
const filters         = ['All', 'MRI_01', 'CT_01', 'Rescheduled']
const headers         = ['Appt ID', 'Machine', 'Patient', 'Date', 'Time', 'Priority', 'Duration', 'Status']

const mriCount        = computed(() => allAppointments.value.filter(a => a.machine_id === 'MRI_01').length)
const ctCount         = computed(() => allAppointments.value.filter(a => a.machine_id === 'CT_01').length)
const rescheduledCount = computed(() => allAppointments.value.filter(a => a.rescheduled).length)
const filtered        = computed(() => {
  if (activeFilter.value === 'All')         return allAppointments.value
  if (activeFilter.value === 'Rescheduled') return allAppointments.value.filter(a => a.rescheduled)
  return allAppointments.value.filter(a => a.machine_id === activeFilter.value)
})

onMounted(async () => {
  try { const { data } = await schedule(); allAppointments.value = data.schedule || [] } catch (e) { console.error(e) }
  loading.value = false
})
</script>
