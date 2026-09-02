<template>
    <el-row class="replay-row-top">
        <el-scrollbar style="width: 100%;">
            <div class="scrollbar-demo-item">
                <Question :question="question" />
                <md-editor v-model="answer.text" @onHtmlChanged="change" @onUploadImg="uploadImg"
                    :toolbarsExclude="toolbarsExclude" />

                <el-dialog v-model="submitDialogVisible" width="30%" :before-close="handleClose">
                    <div>
                        <div>
                            <el-radio v-model="answer.enableComment" label="1" size="large">开启评论</el-radio>
                            <el-radio v-model="answer.enableComment" label="2" size="large">关闭评论</el-radio>
                        </div>
                        <div style="margin: 5px 0" />
                        <div>
                            <el-radio v-model="answer.enableRewward" label="1" size="large">开启打赏</el-radio>
                            <el-radio v-model="answer.enableRewward" label="0" size="large">关闭打赏</el-radio>
                        </div>
                        <div style="margin: 5px 0" />
                        <div>
                            <el-radio v-model="enableShare" label="1" size="large">推送给关注的人</el-radio>
                            <el-radio v-model="enableShare" label="0" size="large">不推送给关注的人</el-radio>
                        </div>
                    </div>
                    <template #footer>
                        <span class="dialog-footer">
                            <el-button @click="submitAnswer" type="primary">发布</el-button>
                            <el-button @click="submitDialogVisible = false">返回</el-button>
                        </span>
                    </template>
                </el-dialog>
            </div>
        </el-scrollbar>
    </el-row>
</template>

<script>
import MdEditor from "md-editor-v3";
import "md-editor-v3/lib/style.css";
import Question from "./commen/Question";
export default {
    components: { MdEditor, Question },
    data() {
        return {
            toolbarsExclude: ["github", "fullscreen", "", "prettier"], // 工具栏排除github
            submitDialogVisible: false, // 提交回答弹窗
            enableShare: "1", //是否分享
            questionId: this.$route.params.value,
            question: "",
            answer: {
                questionId: "",
                text: "",
                userId: "",
                enableComment: "1", //是否允许评论
                enableRewward: "1", //是否允许打赏
            },
            webSocket: null,
        };
    },
    created() {
        if (this.global.checkUserLogin()) {
            this.webSocket = this.global.initWebsocket();
        }
    },
    methods: {
        getQuestionById(questionId) {
            this.axios.get("/question/getQuestionById?questionId=" + questionId).then((res) => {
                if (res.data.code === 200) {
                    this.question = res.data.data;

                }
            });
        },
        submitAnswer() {
            if (!this.global.checkUserLogin()) {
                this.$message.error("请先登录");
                return;
            }
            this.answer.questionId = this.questionId;
            this.answer.userId = this.global.user.userId;
            console.log(this.answer);
            this.axios.post("/answer/addAnswer", this.answer).then((res) => {
                console.log(res.data);
                if (res.data.code === 200) {
                    this.$message.success("回答成功");
                    this.submitDialogVisible = false;
                    this.replayMessage();
                }
            });
        },
        // 提交回答后推送消息,通知提问的人
        replayMessage() {
            const userMessage = {
                userId: this.global.user.userId,
                acceptUserId: this.question.userId,
                sign: "回答了你的问题",
                message: this.question.problem
            }
            this.webSocket.send(JSON.stringify(userMessage));
        },
        change(text) {
            console.log(text);
        },
        uploadImg(fileList) {
            console.log(fileList);
            const param = new FormData();
            param.append("file", fileList[0]);
            this.axios
                .post("/user/uploadImg", param, {
                    headers: {
                        "Content-Type": "multipart/form-data"
                    }
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        console.log(res.data);
                        this.answer.text += `![](${this.global.picIp + res.data.msg})`;
                    } else {
                        this.$message.error(res.data.msg);
                    }
                })
                .catch((err) => {
                    this.$message.error("网络错误");
                });

        },
        imgDel(file) {
            console.log(file);
        },
        // 初始化发布按钮
        submitInit() {
            const str = "发布";
            const newDiv = document.createElement("div");
            newDiv.title = str;
            newDiv.className = "md-toolbar-item";
            newDiv.style.height = "30px";
            newDiv.style.backgroundColor = "#fff";

            const newBtn = document.createElement("el-button");
            newBtn.innerHTML = str;
            newBtn.className = "el-button el-button--primary myBtn";
            newBtn.setAttribute("type", "button");

            newDiv.appendChild(newBtn);
            document.querySelector(".md-toolbar-right").appendChild(newDiv);
            document.querySelector(".myBtn").addEventListener("click", () => {
                this.submitDialogVisible = true;
            });
        },
    },
    mounted() {
        this.submitInit();
        this.getQuestionById(this.questionId);
    },
};
</script>

<style scoped>
.replay-row-top {
    padding-left: 10px;
    height: 100%;
    overflow: auto;
}

.scrollbar-demo-item {
    align-items: center;
    justify-content: center;
    margin: 10px;
    border-radius: 4px;
}

::v-deep .md-toolbar-wrapper .md-toolbar {
    justify-content: normal !important;
}

::v-deep .el-card {
    border: 0;
}
</style>