import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/diary',
      name: 'diary',
      component: () => import('../views/DiaryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isAuthenticated = !!token
  
  console.log('Router guard check:', {
    to: to.path,
    from: from.path,
    token: token ? token.substring(0, 20) + '...' : null,
    isAuthenticated,
    requiresAuth: to.meta.requiresAuth,
    timestamp: new Date().toISOString()
  })
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log('Auth required but no token, redirecting to login')
    next('/login')
  } else if (to.path === '/login' && isAuthenticated) {
    // 이미 로그인된 상태에서 로그인 페이지 접근 시 diary로 리다이렉트
    console.log('User authenticated, redirecting from login to diary')
    next('/diary')
  } else {
    console.log('Router guard allowing navigation')
    next()
  }
})

export default router