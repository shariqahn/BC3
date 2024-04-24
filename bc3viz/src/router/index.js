import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/precipitation',
      name: 'precipitation',
      component: () => import('../views/Precipitation.vue')
    },
    {
      path: '/temperature',
      name: 'temperature',
      component: () => import('../views/Temperature.vue')
    },
    // todo change this to a real home page
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Temperature.vue')
    }
  ]
})

export default router
