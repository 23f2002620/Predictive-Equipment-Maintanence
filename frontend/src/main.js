import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import './style.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',              component: () => import('./views/Dashboard.vue') },
    { path: '/machine/:id',   component: () => import('./views/MachineDetail.vue') },
    { path: '/schedule',      component: () => import('./views/Schedule.vue') },
    { path: '/agent-log',     component: () => import('./views/AgentLog.vue') },
    { path: '/vendors',       component: () => import('./views/Vendors.vue') },
  ],
})

createApp(App).use(createPinia()).use(router).mount('#app')
