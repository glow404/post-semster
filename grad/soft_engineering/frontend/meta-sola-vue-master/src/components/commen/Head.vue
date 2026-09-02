<template>
    <el-menu class="el-menu-demo" mode="horizontal" @select="handleSelect" :ellipsis="false">
        <el-col :span="5">
            <el-menu-item index="1">MetaSola</el-menu-item>
        </el-col>
        <el-col :span="8">
            <el-sub-menu class="head-search" index="2" ref="barparent" :popper-offset="4">
                <template #title class="head-search">
                    <el-input v-model="input4" class="w-50 m-2" placeholder="Type something">
                        <template #suffix>
                            <el-icon class="el-input__icon">
                                <search />
                            </el-icon>
                        </template>
                    </el-input>
                </template>
                <el-menu-item class="head-search-item">item one</el-menu-item>
                <el-menu-item index="2-2">item two</el-menu-item>
                <el-menu-item index="2-3">item three</el-menu-item>
            </el-sub-menu>
        </el-col>
        <el-col :span="4">
            <el-menu-item>
                <el-button type="primary" @click="dialogVisible = true">提问</el-button>
                <el-dialog v-model="dialogVisible" width="45%" :before-close="handleClose">
                    <div style="padding-top: 35px">
                        <el-input type="textarea" v-model="question.problem" :autosize="{ minRows: 1, maxRows: 2 }"
                            placeholder="请输入你的问题" clearable maxlength="30" show-word-limit class="create-question"
                            style="width: 100%" aria-required="true" />
                        <div style="margin: 20px 0" />
                        <el-input type="textarea" v-model="question.describe" :autosize="{ minRows: 4 }"
                            placeholder="请输入你的描述" clearable style="width: 100%" />
                    </div>
                    <template #footer>
                        <span class="dialog-footer">
                            <el-button type="primary" @click="submitQuestion()">提问</el-button>
                            <el-button @click="dialogVisible = false">关闭</el-button>
                        </span>
                    </template>
                </el-dialog>
            </el-menu-item>
        </el-col>
        <el-col :span="2">
            <el-menu-item class="head-notice" @mouseenter="showNotice" @mouseleave="hideNotice">
                <el-icon>
                    <bell-filled />
                </el-icon>
                <div class="nav-counter">{{ unreadNoticeCount }}</div>
            </el-menu-item>

            <transition name="Fade">
                <el-space wrap class="notice" v-if="noticeShow" @mouseenter="showNotice" @mouseleave="hideNotice" >
                    <el-card class="box-card" style="width: 150px">
                        <template #header>
                            <div class="card-header">
                                <el-button class="button" @click="showInvitationMessage(this.global.user.userId)" type="text">
                                    <el-icon>
                                        <fold />
                                    </el-icon>
                                </el-button>
                                <span style="color: #ebebeb">|</span>
                                <el-button class="button" @click="showOtherMessage(this.global.user.userId)" type="text">
                                    <el-icon>
                                        <more />
                                    </el-icon>
                                </el-button>
                            </div>
                        </template>
                        <div v-for="userMessage in userMessagePage.records" class="notice-text">
                            <span class="notice-user">{{ userMessage.nickname }}</span>
                            <span style="margin: 0 5px;"> {{userMessage.sign}} </span>
                            <span v-if="userMessage.isRead === 1" class="notice-question-unread">{{ userMessage.message
                            }}</span>
                            <span v-else class="notice-question-read">{{ userMessage.message }}</span>

                        </div>
                    </el-card>
                    <div class="" style="height: 20px"></div>
                </el-space>
            </transition>
        </el-col>

        <el-col :span="2">
            <el-menu-item class="head-message" @mouseenter="showMessage" @mouseleave="hideMessage">
                <el-icon>
                    <chat-dot-round />
                </el-icon>
                <div class="nav-counter">4</div>
            </el-menu-item>

            <transition name="Fade">
                <el-space wrap class="message" v-if="messageShow" @mouseenter="showMessage" @mouseleave="hideMessage">
                    <el-card class="box-card" style="width: 150px">
                        <template #header>
                            <div class="message-head">我的私信</div>
                        </template>

                        <div v-for="o in 6" :key="o" class="notice-text scrollbar-demo-item">
                            <el-col :span="4">
                                <el-avatar style="margin-top: 6px; margin-right: 5px" :size="30"
                                    src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
                            </el-col>
                            <el-col :span="20">
                                <div class="message-text">
                                    <div class="message-user">邀请你回答:</div>
                                    <p class="message-question">
                                        {{ " " + o }}
                                    </p>
                                </div>
                            </el-col>
                        </div>
                    </el-card>
                    <div class="" style="height: 20px"></div>
                </el-space>
            </transition>
        </el-col>
        <el-col :span="3">
            <el-menu-item>
                <el-dropdown ref="dropdown">
                    <el-avatar :size="27" :src="this.global.picIp + this.global.user.picture" @click="loginDialog(1)" />
                    <span style="margin-left: 5px">{{ this.global.checkUserLogin() ? this.global.user.nickname : "未登录" }}</span>
                    <template #dropdown >
                        <el-dropdown-menu>
                            <el-dropdown-item v-if="isLogin" >修改密码</el-dropdown-item>
                            <el-dropdown-item v-if="isLogin" @click="loginOut">退出登录</el-dropdown-item>
                            <el-dropdown-item v-if="!isLogin" @click="loginDialog(1)">登录</el-dropdown-item>

                        </el-dropdown-menu>
                    </template>
                </el-dropdown>

                <Login @closeLogin="loginDialog" @loginInfo="loginInfo" :loginDialogVisible="loginDialogVisible" />
                <Register @closeRegister="registerDialog" :registerDialogVisible="registerDialogVisible" />
            </el-menu-item>
        </el-col>
    </el-menu>
</template>

<script>
import Message from "./Right.vue";
import Register from "../user/Register.vue";
import Login from "../user/Login.vue";
import {BellFilled, ChatDotRound, Fold, More} from "@element-plus/icons-vue";

export default {
    components: {ChatDotRound, More, Fold, BellFilled, Message, Register, Login },
    data() {
        return {
            isLogin: false,
            isOtherMessage:false,
            noticeShow: false, // 是否显示提醒
            unreadNoticeCount: 0, // 未读通知消息数量
            messageShow: false, // 是否显示私信
            timer: null, // 控制提醒和私信显示的定时器
            input4: "", // 搜索框
            dialogVisible: false, // 是否显示提问弹窗
            loginDialogVisible: false, // 是否显示登录弹窗
            registerDialogVisible: false, // 是否显示注册弹窗
            question: {
                userId: "",
                problem: "", // 提问内容
                describe: "", // 提问描述
            },
            userMessagePage: {
                userId: "",
                username: "", // 用户名
                message: "", // 私信内容
            },
            acceptMessage: {
                sign:"",
                userId: "",
                nickname: "123",
                message: "今天天气不错",
                acceptUserId: "",
                createTime: "",
                isRead: "",
            },
            username: "123456", // 用户名
            password: "123456", // 密码
            webSocket: null, // websocket对象
        };
    },
    created() {
        if (this.global.checkUserLogin()) {
            this.showInvitationMessage(this.global.user.userId);
            this.initWebsocket();
            this.getUnreadNoticeCount(this.global.user.userId);
            this.isLogin=true;
        }


    },
    methods: {
        //注册弹窗 0关闭 1打开 2关闭自己打开另一个
        registerDialog(data) {
            if (data == 1) {
                this.registerDialogVisible = true;
            } else if (data == 0) {
                this.registerDialogVisible = false;
            } else {
                this.registerDialogVisible = false;
                this.loginDialog(1)
            }
        },
        //登录弹窗 0关闭 1打开 2关闭自己打开另一个
        loginDialog(data) {
            if(this.global.checkUserLogin()){
                this.loginDialogVisible = false;
                return;
            }
            if (data == 1) {
                this.loginDialogVisible = true;
            } else if (data == 0) {
                this.loginDialogVisible = false;
            } else {
                this.loginDialogVisible = false;
                this.registerDialog(1);
            }
        },
        // 显示提醒
        showNotice() {
            clearTimeout(this.timer);
            this.messageShow = false;
            this.noticeShow = true;
        },
        // 隐藏提醒
        hideNotice() {
            //延迟1s执行，返回定时器
            //创建一个定时器
            clearTimeout(this.timer);
            this.timer = setTimeout(() => {
                this.noticeShow = false;
                clearTimeout(this.timer);
            }, 250);
        },
        // 显示私信
        showMessage() {
            clearTimeout(this.timer);
            this.noticeShow = false;
            this.messageShow = true;
        },
        // 隐藏私信
        hideMessage() {
            clearTimeout(this.timer);
            this.timer = setTimeout(() => {
                this.messageShow = false;
                clearTimeout(this.timer);
            }, 250);
        },
        //获取邀请回答通知消息
        showInvitationMessage(userId) {
            this.isOtherMessage=false;
            this.axios
                .get("/userMessage/getInvitationMessage", {
                    params: {
                        userId: userId,
                        current: 1,
                        size: 10,
                    },
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.userMessagePage = res.data.data;
                    }
                });
        },
        //获取其他通知消息
        showOtherMessage(userId){
            this.isOtherMessage=true;
            this.axios
                .get("/userMessage/getOtherMessage", {
                    params: {
                        userId: userId,
                        current: 1,
                        size: 10,
                    },
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.userMessagePage = res.data.data;
                    }
                });
        },
        //登录
        loginInfo(data) {
            this.global.user = data;
            this.showInvitationMessage(this.global.user.userId);
            this.getUnreadNoticeCount(this.global.user.userId);
            this.isLogin = true;
        },
        //退出登录
        loginOut() {
            this.global.loginOut();
            this.userMessagePage = "";
            this.isLogin = false;
            this.unreadNoticeCount = 0;
        },
        //提个问题
        submitQuestion() {
            if (!this.global.checkUserLogin()) {
                this.$message.error("请先登录");
                return;
            }
            if(this.question.problem==""){
                this.$message.error("请输入问题");
                return;
            }
            this.question.userId = this.global.user.userId;
            this.axios.post("/question/addQuestion", this.question).then((res) => {
                if (res.data.code == 200) {
                    this.$message.success(res.data.msg);
                    this.dialogVisible = false;
                } else {
                    this.$message.error(res.data.msg);
                }
            });
        },
        //查询未读通知消息的个数
        getUnreadNoticeCount(userId) {
            this.axios.get("/userMessage/getUnreadUserMessageCount?userId=" + userId).then((res) => {
                if (res.data.code == 200) {
                    this.unreadNoticeCount = res.data.data;
                }
            })
        },
        //websocket接收消息
        acceptUserMessage(data) {
            const userMessage = JSON.parse(data);
            this.acceptMessage.sign=userMessage.sign;
            this.acceptMessage.userId = userMessage.userId;
            this.acceptMessage.nickname = userMessage.nickname;
            this.acceptMessage.message = userMessage.message;
            this.acceptMessage.acceptUserId = userMessage.acceptUserId;
            this.acceptMessage.isRead=1;
            console.log(userMessage.sign=='邀请你回答')
            if(userMessage.sign=='邀请你回答'&&this.isOtherMessage==false){
                this.userMessagePage.records.unshift(this.acceptMessage);
            }else if(userMessage.sign!='邀请你回答'&&this.isOtherMessage==true){
                this.userMessagePage.records.unshift(this.acceptMessage);
            }
            this.unreadNoticeCount++;
            
        },
        //消息通知的websocket通知
        initWebsocket() {
            this.webSocket = this.global.initWebsocket();
            if (this.webSocket == "") {
                return;
            }
            this.webSocket.onmessage = (event) => {
                this.acceptUserMessage(event.data);
            };

        },
        // changeDropdown(data) {
            
        //     const dropdown = this.$refs.dropdown;
        //     console.log(dropdown);
        //     if (this.global.checkUserLogin()) {
        //         dropdown.handleClose();
        //     } else {
        //         dropdown.handleOpen();
        //     }
        // }
    },
    mounted() {
        //初始化热点和搜索历史和搜索框一样宽
        const parentClientWidth = this.$refs.barparent.$el.clientWidth;
        document.querySelector(".head-search-item").style.width =
            parentClientWidth + "px";
    },
};
</script>
<style scoped>
.el-menu-demo {
    height: 60px;
    width: 100%;
}

.head-search {
    padding: 0 !important;
    background-color: #ffffff !important;
    border: 0;
}

.dialog-footer button:first-child {
    margin-right: 10px;
}

::v-deep .el-dialog__headerbtn {
    top: -5px;
    right: -5px;
    width: 40px;
    height: 40px;
}

::v-deep .el-dialog__body {
    padding: 0 20px;
    margin-top: 12px;
}

.create-question {
    display: block;
}

::v-deep .create-question .el-textarea__inner {
    resize: none;
}

.head-notice {
    position: absolute;
}

.head-message {
    position: absolute;
}

.message {
    z-index: 100;
    top: 50px;
    left: -113px;
    width: 360px;
    background-color: #ffffff;
    display: block;
    position: relative;
}

.message-head {
    text-align: center;
    line-height: 35px;
}

.message-text {
    float: left;
}

.message-question,
.message-user {
    margin: 0;
    font-size: 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    -webkit-line-clamp: 1;
    word-wrap: break-word;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    line-height: 20px;
}

.notice {
    z-index: 100;
    top: 50px;
    left: -140px;
    width: 360px;
    background-color: #ffffff;
    display: block;
    position: relative;
}

.notice-text {
    padding: 5px 0;
    font-size: 14px;
}

.notice-user {
    color: #1e569c;
    cursor: pointer;
}

.notice-question-unread {
    color: #1e569c;
    cursor: pointer;
}

.notice-question-read {
    color: #7a7b78;
    cursor: pointer;
}

.box-card {
    margin: 0;
}

.card-header>button {
    width: 48%;
}

.el-menu-item {
    background-color: #ffffff !important;
    border: 0;
}

/* login,register */
::v-deep .el-dialog__header {
    padding: 0;
    margin: 0;
    text-align: center;
}

.currect {
    margin-top: 16px !important;
    color: green !important;
    font-size: 25px !important;
    display: none;
}

.error {
    margin-top: 16px !important;
    color: red !important;
    font-size: 25px !important;
}

.avatar-uploader .avatar {
    width: 60px;
    height: 60px;
    display: block;
}

::v-deep .el-sub-menu__icon-arrow {
    display: none;
}

::v-deep .el-sub-menu__title {
    background-color: #ffffff !important;
    padding: 0;
}

::v-deep .el-space.el-space--horizontal.notice {
    box-shadow: var(--el-box-shadow-light);
}

::v-deep .el-space.el-space--horizontal.message {
    box-shadow: var(--el-box-shadow-light);
    max-width: 300px;
}

::v-deep .el-space__item {
    margin: 0 !important;
    padding: 0 !important;
}

::v-deep .el-card.is-always-shadow.box-card {
    border: 0;
    box-shadow: none;
}

::v-deep .el-card__header {
    padding: 0;
}

::v-deep .el-card__body {
    max-height: 220px;
    overflow: auto;
}

::v-deep .el-tooltip__trigger{
    display: flex;
    align-items: center;
}

/* 红点消息数量 */
.nav-counter {
    position: absolute;
    min-width: 12px;
    height: 12px;
    line-height: 12px;
    margin-top: -11px;
    margin-left: 12px;
    font-size: 5px;
    font-weight: normal;
    color: white;
    text-align: center;
    text-shadow: 0 1px rgba(0, 0, 0, 0.2);
    background: #e23442;
    border: 1px solid #911f28;
    border-radius: 50%;
    background-image: -webkit-linear-gradient(top, #e8616c, #dd202f);
    background-image: -moz-linear-gradient(top, #e8616c, #dd202f);
    background-image: -o-linear-gradient(top, #e8616c, #dd202f);
    background-image: linear-gradient(to bottom, #e8616c, #dd202f);
    -webkit-box-shadow: inset 0 0 1px 1px rgba(255, 255, 255, 0.1),
        0 1px rgba(0, 0, 0, 0.12);
    box-shadow: inset 0 0 1px 1px rgba(255, 255, 255, 0.1),
        0 1px rgba(0, 0, 0, 0.12);
}

/* 将红的变蓝点 */
.nav-counter-green {
    background: #75a940;
    border: 1px solid #42582b;
    background-image: -webkit-linear-gradient(top, #8ec15b, #689739);
    background-image: -moz-linear-gradient(top, #8ec15b, #689739);
    background-image: -o-linear-gradient(top, #8ec15b, #689739);
    background-image: linear-gradient(to bottom, #8ec15b, #689739);
}

/* 滚动条 */
.scrollbar-demo-item {
    align-items: center;
    justify-content: center;
    margin: 10px;
    border-radius: 4px;
}

/* 淡入淡出的css */
.Fade-enter-from,
.Fade-leave-to {
    opacity: 0;
}

.Fade-enter-to,
.Fade-leave {
    opacity: 1;
}

.Fade-enter-active,
.Fade-leave-active {
    transition: all 0.3s;
}
</style>

<style>
.avatar-uploader .el-upload {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
    border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 178px;
    height: 178px;
    text-align: center;
}
</style>
