<template>
    <dev>
        <el-container>
            <el-header>
                <el-menu router :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">
                    <el-menu-item :index="$router.options.routes[0].children[2].path" >事务管理</el-menu-item>
                    <el-menu-item :index="$router.options.routes[0].children[0].path">文物列表</el-menu-item>
                    <el-menu-item :index="$router.options.routes[0].children[4].path">新增文物</el-menu-item>
                    <el-submenu>
                        <template slot="title">个人中心</template>
                        <el-menu-item :index="$router.options.routes[0].children[1].path">我的信息</el-menu-item>
                        <el-menu-item @click="logout()">登出</el-menu-item>
                    </el-submenu>
                </el-menu>
            </el-header>
            <el-main>
                <el-container style="width: 80%; border: 1px solid #eee;margin: 0 auto;">
                    <router-view></router-view>
                </el-container>
            </el-main>
            <el-footer>
                <el-row :gutter="12">
                    <el-col :span="8">
                        <el-card shadow="hover">
                            博物馆今日总人数: 27242人
                        </el-card>
                    </el-col>
                    <el-col :span="8">
                        <el-card shadow="hover">
                            [公告]博物馆因疫情影响下周闭馆
                        </el-card>
                    </el-col>
                    <el-col :span="8">
                        <el-card shadow="hover">
                            [公告]博物馆新增276个古文物
                        </el-card>
                    </el-col>
                </el-row>
            </el-footer>
        </el-container>
    </dev>
</template>

<script>
    export default {
        methods: {
            logout(){
                this.$router.push('/')
            }
        }
    }
</script>

<style scoped>

</style>