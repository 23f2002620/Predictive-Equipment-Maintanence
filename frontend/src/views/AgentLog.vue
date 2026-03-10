<template>
  <div style="padding:32px 28px; background:var(--white); min-height:100vh;">

    <div class="fade-up" style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:16px; margin-bottom:28px;">
      <div>
        <p style="font-size:12px; text-transform:uppercase; letter-spacing:0.1em; color:var(--blue); font-weight:700; margin-bottom:6px;">Autonomous Agent</p>
        <h1 style="font-size:28px; font-weight:800; color:var(--gray-900); letter-spacing:-0.6px;">Activity Log</h1>
        <p style="font-size:14px; color:var(--gray-400); margin-top:6px;">LangGraph pipeline · Vendor tickets · Reschedules · Notifications</p>
      </div>
      <div style="display:flex; gap:8px;">
        <button @click="runAll" :disabled="running" class="btn-primary" style="font-size:12px;">
          <div v-if="running" class="spinner" style="width:12px; height:12px; border-top-color:white; border-color:rgba(255,255,255,0.3); border-width:1.5px;"></div>
          {{ running ? 'Running…' : '⚡ Run All Agents' }}
        </button>
        <button @click="load" class="btn-secondary" style="font-size:12px;">Refresh</button>
      </div>
    </div>

    <Transition name="slide">
      <div v-if="agentResult" class="card fade-in" style="padding:22px; margin-bottom:20px;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; flex-wrap:wrap; gap:8px;">
          <h3 style="font-size:15px; font-weight:700; color:var(--gray-900); letter-spacing:-0.2px;">Latest Agent Run</h3>
          <button @click="agentResult = null" class="btn-ghost" style="font-size:12px;">Dismiss</button>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px,1fr)); gap:12px;">
          <div v-for="(res, mid) in agentResult.results" :key="mid"
            style="background:var(--gray-50); border:1px solid var(--gray-100); border-radius:var(--radius-md); padding:16px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
              <span style="font-size:14px; font-weight:800; color:var(--gray-900);">{{ mid }}</span>
              <RiskBadge :code="res.risk?.risk_code" />
            </div>
            <div style="display:flex; flex-direction:column; gap:4px; margin-bottom:10px;">
              <p v-for="a in res.actions" :key="a" style="font-size:12px; color:var(--gray-600); line-height:1.6;">{{ a }}</p>
            </div>
            <div style="display:flex; gap:6px; flex-wrap:wrap;">
              <span v-if="res.vendor_ticket"
                style="font-size:11px; background:var(--green-light); color:#1a7f3c; padding:3px 10px; border-radius:980px; font-weight:600; border:1px solid rgba(52,199,89,0.2);">
                ✓ {{ res.vendor_ticket?.ticket?.ticket_id }}
              </span>
              <span v-if="res.reschedules?.length"
                style="font-size:11px; background:var(--blue-light); color:var(--blue); padding:3px 10px; border-radius:980px; font-weight:600; border:1px solid rgba(0,113,227,0.15);">
                ✓ {{ res.reschedules.length }} rescheduled
              </span>
              <span v-if="res.notification?.notification"
                style="font-size:11px; background:var(--purple-light); color:var(--purple); padding:3px 10px; border-radius:980px; font-weight:600; border:1px solid rgba(175,82,222,0.2);">
                ✓ Notified: {{ res.notification.notification.recipients?.join(', ') }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <div style="display:flex; gap:0; border-bottom:1px solid var(--gray-100); margin-bottom:20px;">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
        style="padding:12px 20px; font-size:13px; font-weight:600; cursor:pointer; border:none; background:transparent; border-bottom:2px solid transparent; margin-bottom:-1px; transition:all 0.2s; font-family:'Manrope',sans-serif; display:flex; align-items:center; gap:6px;"
        :style="activeTab === tab.key
          ? 'border-bottom-color:var(--blue); color:var(--blue);'
          : 'color:var(--gray-400);'">
        {{ tab.label }}
        <span v-if="counts[tab.key]"
          style="font-size:11px; padding:1px 7px; border-radius:980px; font-weight:700;"
          :style="activeTab === tab.key
            ? 'background:var(--blue-light); color:var(--blue);'
            : 'background:var(--gray-100); color:var(--gray-500);'">
          {{ counts[tab.key] }}
        </span>
      </button>
    </div>

    <div v-if="activeTab === 'tickets'">
      <div v-if="!logs.vendor_tickets?.length"
        style="text-align:center; padding:60px 20px; color:var(--gray-400);">
        <div style="width:48px; height:48px; border-radius:14px; background:var(--gray-100); display:flex; align-items:center; justify-content:center; margin:0 auto 14px;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--gray-300)" stroke-width="2"><path d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"/></svg>
        </div>
        <p style="font-size:14px; font-weight:600; color:var(--gray-600); margin-bottom:4px;">No vendor tickets yet</p>
        <p style="font-size:13px;">Run the agent to auto-generate service tickets</p>
      </div>
      <div v-else style="display:flex; flex-direction:column; gap:12px;">
        <div v-for="t in logs.vendor_tickets" :key="t.ticket_id" class="card" style="padding:20px;">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
              <span style="font-size:13px; font-weight:800; color:var(--blue);">{{ t.ticket_id }}</span>
              <!-- FIX: CRITICAL badge was 'bg-gray-800 text-gray-300' — now uses proper colors -->
              <span style="padding:3px 10px; border-radius:980px; font-size:11px; font-weight:700;"
                :style="t.urgency === 'CRITICAL'
                  ? 'background:var(--purple-light); color:var(--purple); border:1px solid rgba(175,82,222,0.2);'
                  : t.urgency === 'HIGH'
                    ? 'background:var(--red-light); color:#c0392b; border:1px solid rgba(255,59,48,0.15);'
                    : 'background:var(--amber-light); color:#b86e00; border:1px solid rgba(255,159,10,0.15);'">
                {{ t.urgency }}
              </span>
              <span style="padding:3px 10px; border-radius:980px; font-size:11px; font-weight:700; background:var(--green-light); color:#1a7f3c; border:1px solid rgba(52,199,89,0.2);">
                {{ t.status }}
              </span>
            </div>
            <span style="font-size:11px; color:var(--gray-400);">{{ t.created_at?.slice(0,19).replace('T',' ') }}</span>
          </div>
          <p style="font-size:13.5px; color:var(--gray-700); margin-bottom:14px; line-height:1.6; background:var(--gray-50); padding:10px 14px; border-radius:9px; border:1px solid var(--gray-100);">{{ t.fault_summary }}</p>
          <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:8px;">
            <div v-for="row in ticketRows(t)" :key="row.l" style="background:var(--gray-50); border:1px solid var(--gray-100); border-radius:9px; padding:10px 14px;">
              <p style="font-size:10px; color:var(--gray-400); font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:3px;">{{ row.l }}</p>
              <p style="font-size:13px; color:var(--gray-800); font-weight:600;">{{ row.v }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'reschedules'">
      <div v-if="!logs.reschedules?.length"
        style="text-align:center; padding:60px 20px; color:var(--gray-400);">
        <p style="font-size:14px; font-weight:600; color:var(--gray-600); margin-bottom:4px;">No reschedules yet</p>
        <p style="font-size:13px;">Run the agent to auto-reschedule affected appointments</p>
      </div>
      <div v-else style="display:flex; flex-direction:column; gap:10px;">
        <div v-for="r in logs.reschedules" :key="r.appointment_id" class="card" style="padding:18px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
          <div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:5px;">
              <span style="font-size:13px; font-weight:800; color:var(--blue);">{{ r.appointment_id }}</span>
              <span style="padding:3px 10px; border-radius:980px; font-size:11px; font-weight:700; background:var(--amber-light); color:#b86e00; border:1px solid rgba(255,159,10,0.15);">{{ r.status }}</span>
              <span v-if="r.patient_notified" style="padding:3px 10px; border-radius:980px; font-size:11px; font-weight:700; background:var(--green-light); color:#1a7f3c; border:1px solid rgba(52,199,89,0.2);">Patient Notified</span>
            </div>
            <p style="font-size:12px; color:var(--gray-500); line-height:1.5;">{{ r.reason }}</p>
          </div>
          <div style="text-align:right;">
            <p style="font-size:10px; text-transform:uppercase; letter-spacing:0.08em; color:var(--gray-400); font-weight:700; margin-bottom:3px;">New Slot</p>
            <p style="font-size:14px; font-weight:800; color:var(--gray-900);">{{ r.new_slot }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'notifications'">
      <div v-if="!logs.notifications?.length"
        style="text-align:center; padding:60px 20px; color:var(--gray-400);">
        <p style="font-size:14px; font-weight:600; color:var(--gray-600); margin-bottom:4px;">No notifications yet</p>
        <p style="font-size:13px;">Run the agent to dispatch team notifications</p>
      </div>
      <div v-else style="display:flex; flex-direction:column; gap:12px;">
        <div v-for="n in logs.notifications" :key="n.notification_id" class="card" style="padding:20px;">
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:13px; font-weight:800; color:var(--blue);">{{ n.notification_id }}</span>
              <span style="padding:3px 10px; border-radius:980px; font-size:11px; font-weight:700; background:var(--purple-light); color:var(--purple); border:1px solid rgba(175,82,222,0.2);">SENT</span>
            </div>
            <span style="font-size:11px; color:var(--gray-400);">{{ n.sent_at?.slice(0,19).replace('T',' ') }}</span>
          </div>
          <div style="background:var(--gray-50); border:1px solid var(--gray-100); border-radius:9px; padding:12px 14px; margin-bottom:14px;">
            <p style="font-size:13px; color:var(--gray-700); line-height:1.6; font-weight:500;">{{ n.recommended_action }}</p>
          </div>
          <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:12px;">
            <div v-for="row in notifRows(n)" :key="row.l" style="background:var(--gray-50); border:1px solid var(--gray-100); border-radius:9px; padding:10px 12px; text-align:center;">
              <p style="font-size:10px; color:var(--gray-400); font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:3px;">{{ row.l }}</p>
              <p style="font-size:13px; font-weight:700; color:var(--gray-800);">{{ row.v }}</p>
            </div>
          </div>
          <div v-if="n.net_saving_inr"
            style="background:var(--green-light); border:1px solid rgba(52,199,89,0.2); border-radius:9px; padding:10px 14px; margin-bottom:10px; display:flex; align-items:center; gap:8px;">
            <span style="font-size:11px; color:#1a7f3c; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;">Net Saving</span>
            <span style="font-size:16px; font-weight:800; color:#1a7f3c; letter-spacing:-0.3px;">₹{{ (n.net_saving_inr / 100000).toFixed(1) }}L</span>
          </div>
          <div style="display:flex; align-items:center; gap:6px;">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--gray-400)" stroke-width="2"><path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
            <span style="font-size:12px; color:var(--gray-400); font-weight:500;">{{ n.recipients?.join(' · ') }}</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import RiskBadge from '../components/RiskBadge.vue'

const { agentLogs, agentRunAll } = useApi()
const logs        = ref({ vendor_tickets: [], reschedules: [], notifications: [] })
const agentResult = ref(null)
const running     = ref(false)
const activeTab   = ref('tickets')
const tabs = [
  { key: 'tickets',       label: 'Vendor Tickets'  },
  { key: 'reschedules',   label: 'Reschedules'     },
  { key: 'notifications', label: 'Notifications'   },
]
const counts = computed(() => ({
  tickets:       logs.value.vendor_tickets?.length  || 0,
  reschedules:   logs.value.reschedules?.length     || 0,
  notifications: logs.value.notifications?.length   || 0,
}))

const ticketRows = t => [
  { l: 'Vendor',   v: t.vendor_name    },
  { l: 'Contact',  v: t.contact_person },
  { l: 'Phone',    v: t.phone          },
  { l: 'Rate',     v: `₹${t.hourly_rate_inr}/hr` },
]
const notifRows = n => [
  { l: 'Risk Tier',  v: n.risk_tier          },
  { l: 'Days Left',  v: n.days_to_failure    },
  { l: 'Confidence', v: `${((n.confidence || 0) * 100).toFixed(0)}%` },
  { l: 'Machine',    v: n.machine_id         },
]

const load = async () => {
  try { const { data } = await agentLogs(); logs.value = data } catch {}
}
const runAll = async () => {
  running.value = true
  try {
    const { data } = await agentRunAll()
    agentResult.value = data
    await load()
  } catch (e) { console.error(e) }
  running.value = false
}

onMounted(load)
</script>
