<template>
    <div >
        <el-col :span="2" style="flex:none">
            <img class="user-img" :src="this.global.picIp + user.picture" />
        </el-col>
        <el-col :span="16">
            <div>{{ user.nickname }}</div>
            <div class="user-identity p-set">
                {{ user.identity }}
            </div>
        </el-col>
        <el-col :span="3">
            <el-button @click="goChat(user.userId)" style="margin: 0 10px" type="danger">
                <el-icon>
                    <Message />
                </el-icon>
                私聊
            </el-button>
        </el-col>
        <el-col :span="3">
            <el-button @click="followOtherUser(user.userId)" type="danger">
                <el-icon>
                    <Plus />
                </el-icon><span v-if="user.isFollow">已</span> 关注
            </el-button>
        </el-col>

    </div>
</template>
<script>
export default{
    props: ["user"],
    created() {
    },
    methods: {
        goChat(userId) {
            this.$GRouter.goChat(userId);
        },
         followOtherUser(userId) {
            if (!this.global.checkUserLogin()) {
                this.$message.error("请先登录");
                return;
            }
            if (this.user.isFollow == false) {
                this.axios.post("/userFollow/follow", {
                    userId: this.global.user.userId,
                    followUserId: userId
                }).then(res => {
                    if (res.data.code == 200) {
                        this.$message.success("关注成功");
                        this.user.isFollow = true;
                    }
                })
            } else {
                this.axios.post("/userFollow/unFollow", {
                    userId: this.global.user.userId,
                    followUserId: userId
                }).then(res => {
                    if (res.data.code == 200) {
                        this.$message.success("取消关注");
                        this.user.isFollow = false;
                    }
                })
            }

        }
    },
}
</script>
<style scoped>
.user-img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
}

.user-identity {
    color: #9e9ea6;
    font-size: 12px;
}

.main button {
    background: #fb7299;
}
</style>