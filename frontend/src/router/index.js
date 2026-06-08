import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/accessories' },
  {
    path: '/accessories',
    component: () => import('@/views/Accessories.vue'),
    meta: { title: '饰品目录' }
  },
  {
    path: '/storage',
    component: () => import('@/views/Storage.vue'),
    meta: { title: '收纳位置' }
  },
  {
    path: '/recommend',
    component: () => import('@/views/Recommend.vue'),
    meta: { title: '智能搭配推荐' }
  },
  {
    path: '/favorites',
    component: () => import('@/views/Favorites.vue'),
    meta: { title: '场合收藏' }
  },
  {
    path: '/statistics',
    component: () => import('@/views/Statistics.vue'),
    meta: { title: '数据统计' }
  },
  {
    path: '/trips',
    component: () => import('@/views/Trips.vue'),
    meta: { title: '旅行/活动搭配行李规划' }
  },
  {
    path: '/tracking',
    component: () => import('@/views/Tracking.vue'),
    meta: { title: '借出与保养追踪' }
  },
  {
    path: '/valuation',
    component: () => import('@/views/Valuation.vue'),
    meta: { title: '估值总览' }
  },
  {
    path: '/certificates',
    component: () => import('@/views/Certificates.vue'),
    meta: { title: '证书档案' }
  },
  {
    path: '/inventory',
    component: () => import('@/views/Inventory.vue'),
    meta: { title: '盘点任务' }
  },
  {
    path: '/inventory-exceptions',
    component: () => import('@/views/InventoryExceptions.vue'),
    meta: { title: '异常处理' }
  },
  {
    path: '/insurance',
    component: () => import('@/views/Insurance.vue'),
    meta: { title: '保险清单' }
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
