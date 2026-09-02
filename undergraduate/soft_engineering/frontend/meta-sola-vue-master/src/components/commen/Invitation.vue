<template>
    <el-dialog v-model="invitationDialogVisible" width="45%" :before-close="closeInvitation">
        <div class="top">
            <span>你可以邀请以下用户</span>
            <el-input v-model="input4" class="w-50 m-2" placeholder="search">
                <template #prefix>
                    <el-icon class="el-input__icon">
                        <search />
                    </el-icon>
                </template>
            </el-input>
        </div>

        <div class="main">
            <el-scrollbar style="width: 100%">
                <div class="scrollbar-demo-item">
                    <div v-for="(user,index) in userPage.records">
                        <el-divider style="margin: 10px 0" />
                        <div class="replay-user">
                            <el-avatar :size="35" :src="this.global.picIp + user.picture" />
                            <span style="margin-left: 5px">{{ user.nickname }}</span>
                            <el-button @click="invitationMessage(user,index)" type="primary" class="invitation-right">
                                邀请回答</el-button>
                        </div>
                    </div>
                </div>
            </el-scrollbar>
        </div>
    </el-dialog>
</template>

<script>
export default {
    name: "Invitation",
    props: ["invitationDialogVisible","problem"],
    setup(props, { emit }) {
        //分解context对象取出emit
        function closeInvitation(data) {
            emit("closeInvitation", data == null ? 0 : data);
        }
        return {
            closeInvitation,
        };
    },
    data() {
        return {
            dialogVisible: true,
            user:"",
            userPage: "",
            invitation:"",
            userMessage: {
                sign:"",
                userId: "",
                nickname: "",
                message: "",
                acceptUserId: "",
            },
            webSocket: "",
        };
    },
    created() {
        this.getUserPage();
        if(this.global.checkUserLogin()){
            this.webSocket=this.global.initWebsocket();
        }
        
    },
    methods: {
        //分页获取用户
        getUserPage() {
            this.axios.post("/user/getUserPage", {
                params: {
                    current: 1,
                    pageSize: 10,
                }
            }).then(res => {
                if (res.data.code == 200) {
                    this.userPage = res.data.data;
                }
            }, err => {
                console.log(err);
            });
        },
        invitationMessage(user,index) {
            if(!this.global.checkUserLogin()){
                this.$message.err("请先登录");
                return;
            }
            this.userMessage.sign="邀请你回答";
            this.userMessage.acceptUserId = user.userId;
            this.userMessage.userId = this.global.user.userId;
            this.userMessage.nickname = this.global.user.nickname;
            this.userMessage.message=this.problem;
            this.send(this.userMessage);
            this.userPage.records.splice(index,1);
            this.$message.success("邀请"+user.nickname+"成功");
        },
        
        send(msg) {
            this.webSocket.send(JSON.stringify(msg));
        }
    },
};
</script>

<style scoped>
.top {
    line-height: 32px;
}

::v-deep .el-input__prefix {
    right: 10px !important;
    left: auto;
}

::v-deep .el-input.el-input--prefix.w-50.m-2 {
    width: 50%;
    float: right;
}

.replay-user {
    display: flex;
    align-items: center;
    position: relative;
}

.invitation-right {
    position: absolute;
    right: 5px;
}

.main {
    width: 100%;
    overflow: auto;
    height: 300px;
}

.scrollbar-demo-item {
    align-items: center;
    justify-content: center;
    margin: 10px;
    border-radius: 4px;
}
</style>