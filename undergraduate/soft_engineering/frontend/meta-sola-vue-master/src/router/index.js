import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(),
    routes: [{
        path: '/',
        component: () =>
            import ('@/components/Content')
    }, {
        path: '/Content',
        component: () =>
            import ('@/components/Content')
    }, {
        path: '/Replay/:value',
        component: () =>
            import ('@/components/Replay')
    }, {
        path: '/DetailReplay/:value',
        component: () =>
            import ('@/components/DetailReplay')
    }, {
        path: '/WriteReplay/:value',
        component: () =>
            import ('@/components/WriteReplay')
    }, {
        path: '/DetailDynamic/:value',
        component: () =>
            import ('@/components/DetailDynamic')
    }, {
        path: '/WriteDynamic',
        component: () =>
            import ('@/components/WriteDynamic')
    }, {
        path: '/test',
        component: () =>
            import ('@/components/commen/Invitation')
    }, {
        path: '/Chat/:value',
        component: () =>
            import ('@/components/user/Chat')
    }, {
        path: '/Mine/:value',
        component: () =>
            import ('@/components/user/Mine'),
    }, {
        path: '/UserInfo',
        component: () =>
            import ('@/components/user/UserInfo')
    }]
})

export default router