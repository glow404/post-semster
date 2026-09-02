<template>
    <el-row class="m-height">
        <div class="m-width m-height" style="display:flex">

            <el-col :span="7" class="chat-left">
                <div class="chat-left-main">
                    <el-input v-model="searchUser" class="m-width" placeholder="Type something">
                        <template #suffix>
                            <el-icon class="el-input__icon">
                                <search />
                            </el-icon>
                        </template>
                    </el-input>
                </div>
                <el-collapse style="border:0;" v-model="activeNames" @change="handleChange">
                    <el-collapse-item title="最近联系" name="1">
                        <div class="user-list ">
                            <el-scrollbar>
                                <div class="scrollbar-demo-item">
                                    <div class="user" v-for="(chat,index) in chatList" @click="initChatMessageList(chat.user.userId,index)">
                                        <el-avatar :size="35" style="min-width:35px" :src="this.global.picIp+chat.user.picture"/>
                                        <div style="margin-left: 5px;">
                                            <div>{{chat.user.nickname}}</div>
                                            <p class="user-message">{{chat.text}}</p>
                                        </div>
                                        <div class="nav-counter" v-show="chat.notReadNum!=0">{{chat.notReadNum}}</div>
                                    </div>
                                </div>
                            </el-scrollbar>
                        </div>
                    </el-collapse-item>
                </el-collapse>
            </el-col>

            <el-col :span="17" class="chat-right">
                <div class="chat-right-top">
                    <el-scrollbar :always="true" ref="content">
                        <div class="scrollbar-demo-item" style="margin-bottom:30px">
                            <div v-for="chat in chatMessageList">
                                <div class='receiver' v-if="this.global.user.userId == chat.userId">
                                    <div><img class='margin-bottom-mini' :src='this.global.picIp + chat.user.picture'>
                                    </div>
                                    <div class='max-div-text'>
                                        <div class='right_triangle '></div>
                                        <span>{{ chat.text }}</span>
                                    </div>
                                </div>
                                <div class='sender' v-else>
                                    <div><img class='margin-bottom-mini' :src='this.global.picIp + chat.user.picture'>
                                    </div>
                                    <div class='max-div-text'>
                                        <div class='left_triangle'></div>
                                        <span> {{ chat.text }}</span>
                                    </div>
                                </div>
                            </div>
                            <el-empty v-if="chatUserIdNow==''"  description="选择好友聊天吧" :image-size="100" />

                        </div>
                    </el-scrollbar>
                </div>

                <div class="chat-right-down">
                    <textarea v-model="chatInput" class="chat-right-down-textarea"
                        placeholder="Type something"></textarea>
                    <div>
                        <el-button type="primary" @click="sendChatMessage()" class="chat-right-down-button">发送
                        </el-button>
                    </div>
                </div>
            </el-col>

        </div>

    </el-row>

</template>
<script>
export default {
    data() {
        return {
            searchUser: "",
            activeNames: ["1"],
            chatList: [],
            chatMessageList: [],
            chatInput: "",
            chatUserIdNow: "",
            chatWebSocket: "",
        };
    },
    created() {
        if(this.global.checkUserLogin()){
            this.initChatUserList(this.global.user.userId);
            this.initWebsocketChat();
            if(this.$route.params.value!="undefined"){
                this.initChatMessageList(this.$route.params.value,null);
            }
        }
        
    },
    methods: {
        //初始聊天的滚动条至于底部
        initChatScroll() {
            this.$nextTick(() => {
                const content = this.$refs["content"];
                content.setScrollTop(content.wrap$.scrollHeight)
            })
        },
        // initChatUser(userId){
        //     this.axios.get('/user/getUserByUserId?userId='+userId).then(res=>{
        //         if(res.data.code==200){
        //             this.chatUserNow=res.data.data;
        //         }
        //     })
        // },
        initChatUserList(userId) {
            this.axios.get('/chat/getChatUserListByUserId?userId='+userId).then(res => {
                if (res.data.code == 200) {
                    this.chatList = res.data.data;
                }
            })
        },
        //初始化聊天列表
        initChatMessageList(toUserId,index) {
            
            this.chatUserIdNow = toUserId;
            this.axios.get('/chat/getChatList', {
                params: {
                    userId: this.global.user.userId,
                    toUserId: toUserId
                }
                }).then(res => {
                if (res.data.code == 200) {
                    this.chatMessageList = res.data.data;
                    this.initChatScroll();
                }
            });
            //若果未读消息数量不为0，则清空未读消息数量
            if(index!=null&&this.chatList[index].notReadNum!=0){
                this.axios.get('/chat/updateChatToIsRead', {
                params: {
                    userId: toUserId,
                    toUserId: this.global.user.userId,
                }
                }).then(res => {
                if (res.data.code == 200) {
                    this.chatList[index].notReadNum=0;
                }
            });
            }
            
        },
        //发送聊天信息
        sendChatMessage() {
            if(this.chatUserIdNow==''){
                this.$message.error("请选择要聊天的好友");
                return;
            }
            if (this.chatInput) {
                const chatMessage = {
                    userId: this.global.user.userId,
                    toUserId: this.chatUserIdNow,
                    user: this.global.user,
                    text: this.chatInput,
                    isRead: 0,
                }
                this.chatMessageList.push(chatMessage);
                this.initChatScroll();
                this.chatWebSocket.send(JSON.stringify(chatMessage));
                this.chatInput = "";
               
            }
        },
        //webSocket接收消息
        acceptUserChat(data){
            const chatMessage = JSON.parse(data);
            if(this.chatUserIdNow==chatMessage.userId){
                chatMessage.isRead = 1;
                this.chatMessageList.push(chatMessage);
                this.initChatScroll();
            }
            this.axios.post('/chat/saveChat',chatMessage).then(res=>{
                if(res.data.code==200){
                    this.initChatUserList(this.global.user.userId);
                }
            })
            

        
        },
        //消息通知的websocket通知
        initWebsocketChat() {
            this.chatWebSocket = this.global.initWebsocketChat();
            if (this.chatWebSocket == "") {
                return;
            }
            this.chatWebSocket.onmessage = (event) => {
                this.acceptUserChat(event.data);
            };

        },
    },
    mounted() {
        this.initChatScroll();

    }

}
</script>
<style scoped>
.m-width {
    width: 100%;
}

.m-right {
    float: right;
}

.m-height {

    height: 100%;
}

.chat-left {
    height: 100%;
    border-right: 1px solid #ccc;
    
}

.chat-left-main {
    margin: 5%;
}

.user-list {
    height: 400px;
    overflow: auto;
}

.user {
    position: relative;
    display: flex;
    align-items: center;
}

.user-message {
    font-size: 10px;
    color: #c0c4cc;
    margin: 0;

    overflow: hidden;
    text-overflow: ellipsis;
    -webkit-line-clamp: 1;
    word-wrap: break-word;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    line-height: 20px;
    cursor: pointer;
    word-break: break-all;
}

.chat-right {
    height: 100%;
    display: inline-table;
}

.chat-right-top {
    width: 100%;
    height: 65%;
    overflow: auto;
    border-bottom: 1px solid #ccc;
    padding-bottom: 5px;
}

.chat-right-down {
    width: 100%;
    height: 35%;

}

.chat-right-down-textarea {
    width: 100%;
    height: 70%;
    border: 0;
    resize: none;
    outline: none;
    border-bottom: 1px solid #ccc;
}

.chat-right-down-button {
    float: right;
}

/* 红点消息数量 */
.nav-counter {
    right: 0;
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

/* 左侧的最近联系 */
::v-deep .el-collapse-item__header {
    margin: 0 5%;
}

/* 滚动条 */
.scrollbar-demo-item {
    align-items: center;
    justify-content: center;
    margin: 10px;
    border-radius: 4px;
}
</style>
<style>
/* 聊天的css */
.margin-bottom-mini {
    margin-bottom: .5em;
    border-radius: 50%;
    width: 40px !important;
    height: 40px !important;
}

.sender {
    clear: both;
}

.sender div:nth-of-type(1) {
    float: left;
}

.sender div:nth-of-type(2) {
    background-color: aquamarine;
    float: left;
    margin: 0 20px 10px 15px;
    padding: 10px 10px 10px 0px;
    border-radius: 7px;
}

.receiver div:first-child img,
.sender div:first-child img {
    width: 50px;
    height: 50px;
}

.max-div-text {
    max-width: 70%;
}

.receiver {
    clear: both;
}

.receiver div:nth-child(1) {
    float: right;
}

.receiver div:nth-of-type(2) {
    float: right;
    background-color: #409eff;
    color: aliceblue;
    margin: 0 10px 10px 20px;
    padding: 10px 0px 10px 10px;
    border-radius: 7px;
}

.left_triangle {
    height: 0px;
    width: 0px;
    border-width: 8px;
    border-style: solid;
    border-color: transparent aquamarine transparent transparent;
    position: relative;
    left: -16px;
    top: 3px;
}

.right_triangle {
    height: 0px;
    width: 0px;
    border-width: 8px;
    border-style: solid;
    border-color: transparent transparent transparent #409eff;
    position: relative;
    right: -16px;
    top: 3px;
}
</style>