<template>
    <el-row class="replay-row-top">
        <el-scrollbar style="width: 100%;">
            <div class="scrollbar-demo-item">
                <Question :question="answer.question" />
                <el-divider />
                <div class="dynamic-user">
                    <el-avatar :size="27" :src="this.global.picIp + answer.user.picture" />
                    <span style="margin-left: 5px">{{ answer.user.nickname }}</span>
                </div>

                <md-editor v-model="answer.text" previewOnly />
                <div style="margin-top: 7px">
                    <el-button type="primary" @click="likeAnswer()" :class="{ liked: liked == 1 }" plain>
                        <el-icon>
                            <caret-top />
                        </el-icon>赞同{{ answer.likeNum }}
                    </el-button>
                    <el-button type="primary" @click="disLikeAnswer()" :class="{ liked: liked == 0 }" plain>
                        <el-icon>
                            <caret-bottom />
                        </el-icon>
                    </el-button>
                    <el-button type="primary" plain>
                        <el-icon>
                            <star />
                        </el-icon>收藏
                    </el-button>
                </div>
                <Comment v-if="answer.enableComment == 1" />
                <el-empty v-else description="评论已关闭" :image-size="100" />
            </div>
        </el-scrollbar>
    </el-row>
</template>

<script>
import MdEditor from "md-editor-v3";
import "md-editor-v3/lib/style.css";
import Question from "./commen/Question";
import Comment from "./commen/Comment";
import {CaretBottom, CaretTop, Star} from "@element-plus/icons-vue";
export default {
    components: {Star, CaretBottom, CaretTop, MdEditor, Question, Comment },
    data() {
        return {
            answerId: this.$route.params.value,
            liked: 2,
            answer: {
                question: "",
                user: {
                    nickname: "",
                    picture: "",
                },
                text: "",
                likeNum: "",
                commentCount: "",
                createTime: "",
                comments: [],
            },
            userLike: {
                userId: "",
                answerId: "",
                isLike: "",
            },
        };
    },
    created() {
        this.getAnswerByAnswerId(this.answerId);
        this.getIsLike();
    },
    methods: {
        getAnswerByAnswerId(answerId) {
            this.axios
                .get("/answer/getAnswerByAnswerId", {
                    params: {
                        answerId: answerId,
                    },
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.answer = res.data.data;
                    }
                    console.log(this.answer);
                });
        },
        change(text) { },
        //移除焦点
        handleClick(event) {
            let target = event.target;
            if (target.nodeName == "SPAN"||target.nodeName == "I") {
                target = event.target.parentNode;
            }
            target.blur();
        },
         //点赞
        likeAnswer() {
            if (!this.global.checkUserLogin()) {
                this.$message.error("请先登录");
                return;
            }

            //点过赞就取消赞
            if (this.liked == 1) {
                this.liked = 2;
                this.userLike.isLike = 2;
                this.answer.likeNum = this.answer.likeNum - 1;
            } else {
                this.userLike.isLike = 1;
                this.liked = 1;
                this.answer.likeNum = this.answer.likeNum + 1;
            }

            this.userLike.userId = this.global.user.userId;
            this.userLike.answerId = this.answerId;

            this.axios
                .post("/userLike/addLike", this.userLike)
                .then((res) => {
                    if (res.data.code == 200) {
                        this.$message.success(res.data.msg);
                        
                        if (this.liked == 1) {
                            const userMessage = {
                                userId: this.global.user.userId,
                                acceptUserId: this.answer.answerId,
                                sign: "赞了你的回答",
                                message: this.answer.question.problem
                            }
                            this.axios.post('/userMessage/addUserMessage', userMessage)
                        }
                        
                    } else {
                        this.$message.error(res.data.msg);
                    }
                });
        },
        //点踩
        disLikeAnswer() {
            if (!this.global.checkUserLogin()) {
                this.$message.error("请先登录");
                return;
            }
            
            //isLike==2取消点踩
            if (this.liked == 0) {
                this.userLike.isLike = 2;
                this.liked = 2;
            } else if (this.liked == 1) {         //点过赞就取消点赞
                this.liked = 0;
                this.userLike.isLike = 0;
                this.answer.likeNum = this.answer.likeNum - 1;
            } else {                              //没点过赞的情况
                this.liked = 0;
                this.userLike.isLike = 0;
            }
            
            this.userLike.userId = this.global.user.userId;
            this.userLike.answerId = this.answerId;
            this.axios
                .post("/userLike/addDislike", this.userLike)
                .then((res) => {
                    if (res.data.code == 200) {
                        this.$message.success(res.data.msg);
                    } else {
                        this.$message.error(res.data.msg);
                    }
                });
        },
        //查询是否点赞，或点踩
        getIsLike() {
            if (!this.global.checkUserLogin()) {
                return;
            }
            const userLike = {
                userId: this.global.user.userId,
                answerId: this.answerId,
            };
            this.axios.post("/userLike/getIsLike", userLike).then((res) => {
                    if (res.data.code == 200) {
                        this.liked = res.data.data;
                    }
                });
        },
    },
};
</script>

<style scoped>
::v-deep .md-preview.default-theme h1,
::v-deep .md-preview.default-theme h2,
::v-deep .md-preview.default-theme h3,
::v-deep .md-preview.default-theme h4,
::v-deep .md-preview.default-theme h5 {
    margin: 10px 0 !important;
}

::v-deep .el-card {
    border: 0;
}

.replay-row-top {
    height: 100%;
    overflow: auto;
}

.scrollbar-demo-item {
    align-items: center;
    justify-content: center;
    margin: 10px;
    border-radius: 4px;
}

.dynamic-user {
    display: flex;
    align-items: center;
    margin-top: 20px;
}
.liked{
    color: #ffffff;
    background-color: #409eff;
}
</style>