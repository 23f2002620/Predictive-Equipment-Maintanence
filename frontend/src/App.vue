<template>
  <div style= height:100vh; overflow:hidden; background:var(--white);">

    <!-- Sidebar -->
    <aside style="width:230px; flex-shrink:0; background:var(--gray-50); border-right:1px solid var(--gray-200); display:flex; flex-direction:column; overflow:hidden;">

      <!-- Logo -->
      <div style="padding:22px 18px 16px;">
        <div style="display:flex; align-items:center; gap:11px;">
          <div style="width:38px; height:38px; border-radius:10px; background:var(--black); display:flex; align-items:center; justify-content:center; box-shadow:var(--shadow-md);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="color:white;">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p style="font-size:15px; font-weight:800; color:var(--gray-900); letter-spacing:-0.3px; line-height:1.1;">MediWatch</p>
            <p style="font-size:10px; color:var(--gray-500); margin-top:1px; font-weight:500; letter-spacing:0.02em;">GKM_11 · FASTENERS</p>
          </div>
        </div>
      </div>

      <div class="divider" style="margin:0 18px;"></div>

      <!-- Nav -->
      <nav style="flex:1; padding:14px 10px; display:flex; flex-direction:column; gap:1px; overflow-y:auto;">
        <p style="padding:0 10px; margin-bottom:8px; font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700;">Overview</p>
        <RouterLink to="/" class="nav-link" :class="{ active: $route.path === '/' }">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/>
            <rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>
          </svg>
          Dashboard
        </RouterLink>

        <p style="padding:0 10px; margin:12px 0 8px; font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700;">Equipment</p>
        <RouterLink to="/machine/MRI_01" class="nav-link" :class="{ active: $route.path === '/machine/MRI_01' }">
          <span style="width:8px; height:8px; border-radius:50%; flex-shrink:0; transition:all 0.3s;"
            :style="{background: riskColors['MRI_01'] || 'var(--gray-300)'}"></span>
          MRI_01 · 3T Scanner
        </RouterLink>
        <RouterLink to="/machine/CT_01" class="nav-link" :class="{ active: $route.path === '/machine/CT_01' }">
          <span style="width:8px; height:8px; border-radius:50%; flex-shrink:0; transition:all 0.3s;"
            :style="{background: riskColors['CT_01'] || 'var(--gray-300)'}"></span>
          CT_01 · Revolution CT
        </RouterLink>

        <p style="padding:0 10px; margin:12px 0 8px; font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700;">Operations</p>
        <RouterLink to="/schedule" class="nav-link" :class="{ active: $route.path === '/schedule' }">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          Patient Schedule
        </RouterLink>
        <RouterLink to="/vendors" class="nav-link" :class="{ active: $route.path === '/vendors' }">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>
          </svg>
          Service Vendors
        </RouterLink>
        <RouterLink to="/agent-log" class="nav-link" :class="{ active: $route.path === '/agent-log' }">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          Agent Log
        </RouterLink>
      </nav>

      <!-- Footer -->
      <div class="divider" style="margin:0 18px;"></div>
      <div style="padding:14px 18px 18px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:5px;">
          <span style="position:relative; display:inline-flex; width:8px; height:8px;">
            <span style="position:absolute; inset:0; border-radius:50%; background:var(--green); animation:ping 2s ease-out infinite; opacity:0.5;"></span>
            <span style="position:relative; width:8px; height:8px; border-radius:50%; background:var(--green);"></span>
          </span>
          <span style="font-size:12px; color:var(--gray-600); font-weight:500;">Agent Active</span>
        </div>
        <!-- FIX: was empty string "" -->
        <p style="font-size:11px; color:var(--gray-400);"></p>
      </div>
    </aside>

    <!-- Main -->
    <main style="flex:1; overflow:auto; background:var(--white);">
      <RouterView v-slot="{ Component }">
        <Transition name="slide" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from './composables/useApi'

const riskColors = ref({})
const COLOR_MAP = {
  NORMAL:               'var(--green)',
  MONITOR:              'var(--amber)',
  SCHEDULE_MAINTENANCE: 'var(--red)',
  CRITICAL:             'var(--purple)',
}
onMounted(async () => {
  try {
    const { data } = await useApi().dashboard()
    data.machines.forEach(m => {
      riskColors.value[m.machine_id] = COLOR_MAP[m.risk.risk_code] || 'var(--gray-300)'
    })
  } catch {}
})
</script>

<style>
@keyframes ping {
  0%   { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(2.4); opacity: 0; }
}
</style>
