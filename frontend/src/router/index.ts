import { createRouter, createWebHistory } from 'vue-router'
import CommunityHomeView from '../views/CommunityHomeView.vue'
import AllSharesView from '../views/AllSharesView.vue'
import ThisMonthView from '../views/ThisMonthView.vue'
import LastMonthView from '../views/LastMonthView.vue'
import RankingsView from '../views/RankingsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: CommunityHomeView,
    },
    {
      path: '/all-shares',
      name: 'all-shares',
      component: AllSharesView,
    },
    {
      path: '/this-month',
      name: 'this-month',
      component: ThisMonthView,
    },
    {
      path: '/last-month',
      name: 'last-month',
      component: LastMonthView,
    },
    {
      path: '/rankings',
      name: 'rankings',
      component: RankingsView,
    },
  ],
})

export default router
