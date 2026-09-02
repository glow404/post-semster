<template>
    <el-col class="border-right" :span="5">

        <el-menu default-active="2" :collapse="isCollapse == true ? false : true" @open="handleOpen" @close="handleClose"
            class="el-menu-vertical-demo">
            <el-switch v-model="isCollapse" style="margin-left:20px" />
            <el-menu-item v-for="(item, i) in catalogue" :index="i + 1" @click="go(i + 1)">
                <el-icon>
                    <location-filled />
                </el-icon>
                <span>{{ item }}</span>
            </el-menu-item>
        </el-menu>
    </el-col>
</template>

<script>
export default {
    name: "Index",
    data() {
        return {
            catalogue: [
                "首页",
                "Replay",
                "DetailReplay",
                "DetailDynamic",
                "WriteReplay",
                "WriteDynamic",
                "Chat",
                "Mine",
            ],
            isCollapse: true,
        };
    },
    methods: {
        go(index) {
            switch (index) {
                case 1:
                   this.$GRouter.goContent();
                    this.$router.push('/Content');
                    break;
                case 2:
                    this.$GRouter.goReplay(64);
                    break;
                case 3:
                    this.$GRouter.goDetailReplay(1);
                    break;
                case 4:
                    this.$GRouter.goDetailDynamic(1);
                    break;
                case 5:
                    this.$GRouter.goWriteReplay(64);
                    break;
                case 6:
                    this.$GRouter.goWriteDynamic();
                    break;
                case 7:
                    this.$GRouter.goChat();
                    break;
                case 8:
                    this.$GRouter.goMine(this.global.user.userId);
                    break;
            }
        },
    },
};
</script>
<style scoped>
.border-right {
    height: 100%;
    border-right: 1px solid #dcdfe6;
}

::v-deep .el-menu.el-menu-vertical-demo {
    border: 0;
}
</style>
