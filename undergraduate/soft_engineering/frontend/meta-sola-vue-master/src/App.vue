<template>
  <el-row class="tac">

    <Head style="height: 10%;" />
    <el-col style="height: 89%;" :span="width">
      <Navigation />
      <router-view></router-view>
    </el-col>
    <Right v-if="show" />
  </el-row>
</template>

<script>
import Navigation from "@/components/commen/Navigation.vue";
import Head from "@/components/commen/Head.vue";
import Right from "@/components/commen/Right.vue";

import { useRouter, onBeforeRouteUpdate } from "vue-router";

//let router = useRouter();
//onBeforeRouteUpdate((to) => { });

export default {
    name: "App",
    components: { Navigation, Head, Right },
    data() {
        return {
            path: window.location.pathname,
            width: 18,
            show: true,
            websocket: "",
            userMessage: {
                userId: "1",
                nackname: "张三",
                message: "今天天气号码",
            }
        };
    },
    methods: {
        init() {
            //判断路由是否包含"WriteReplay"
            if (
                window.location.pathname.indexOf("WriteReplay") > -1 ||
                window.location.pathname == "/WriteDynamic"
            ) {
                this.width = 24;
                this.show = false;
            } else {
                this.width = 18;
                this.show = true;
            }
        },
        initUser() {
            const userInfo = JSON.parse(localStorage.getItem("userInfo"));
            if (userInfo == null || userInfo == undefined) {
                return;
            }
            this.global.user = userInfo.user;
        },
        //移除el-button的焦点
        handleClick(event) {
            let target = event.target;
            if (target.nodeName == "SPAN" || target.nodeName == "I") {
                target = event.target.parentNode;
            }
            target.blur();
        },
    },
    mounted() {
        
        //两秒后执行
        setTimeout(() => {
            const btnList = document.querySelectorAll(".el-button");
            for (let i = 0; i < btnList.length; i++) {
                btnList[i].addEventListener("mouseleave", this.handleClick);
            }
        }, 1000);
        //移除所有el-button点击后的焦点


    },
    created() {
        this.init();
        this.initUser();

    },
    watch: {
        $route() {
            this.init();
        },
    },
};
</script>

<style scoped>
#app {
    height: 100%;
}

.tac {
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    min-width: 1100px;
    /* height: 100%;
  width: 100%; */
}

* {
    margin: 0;
    padding: 0;
}
</style>
