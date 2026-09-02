<template>
    <el-empty v-if="commentCount == 0" description="暂时还没有评论，快来抢沙发吧" :image-size="100" />
    <el-card class="box-card">
        <div class="comment-head">
            <span class="comment-sort">
                <el-icon style="margin-right: 5px">
                    <sort />
                </el-icon>
                排序方法
            </span>
            <span>{{ commentCount == undefined ? 0 : commentCount }}条评论</span>
        </div>
        <el-divider />
        <div class="comment-body" v-for="(comment, parentIndex) in commentPage.records">
            <div class="comment-user">
                <el-avatar :size="25" :src="this.global.picIp + comment.user.picture" />
                <span class="user-name">{{ comment.user.nickname }}</span>
                <span v-if="comment.user.userId == UserId || comment.user.userId == UserId"
                    style="color: #9590a6">(作者)</span>
                <span v-if="comment.parentId != null" style="color: #9590a6; margin-left: 5px">回复</span>
                <span v-if="comment.parentId != null" style="margin-left: 5px">{{
                        comment.parentUser.nickname
                }}</span>
                <span style="color: #9590a6; margin-left: 5px">{{ comment.createTime }}</span>
            </div>
            <div class="comment-text">
                {{ comment.text }}
                <div style="margin-top: 7px">
                    <el-button type="primary"  @click="likeComment(
                        comment.commentId,
                        null,
                        parentIndex,
                        comment.user.userId,
                        comment.text
                    )" :class="{ liked: comment.isLike == 1 }" size="small" plain>
                        <el-icon>
                            <caret-top />
                        </el-icon>赞同{{ comment.likeNum }}
                    </el-button>
                    <el-button type="primary"
                        @click="disLikeComment(comment.commentId, null, parentIndex)"
                        :class="{ liked: comment.isLike == 0 }" size="small" plain>
                        <el-icon>
                            <caret-bottom />
                        </el-icon>
                    </el-button>
                    <el-button @click="replay(comment.userId, comment.user.nickname)" style="border: 0" size="small">
                        <el-icon>
                            <chat-dot-round />
                        </el-icon>回复
                    </el-button>
                </div>
            </div>
            <div class="comment-body-child" v-if="comment.childComments.length > 0">
                <div class="comment-child-item" v-for="(childComment, index) in comment.childComments">
                    <div class="comment-user">
                        <el-avatar :size="25" :src="this.global.picIp + childComment.user.picture" />
                        <span class="user-name">{{ childComment.user.nickname }}</span>
                        <span v-if="
                            childComment.user.userId == this.UserId ||
                            childComment.userId == this.UserId
                        " style="color: #9590a6">(作者)</span>
                        <span v-if="childComment.parentId != null" style="color: #9590a6; margin-left: 5px">回复</span>
                        <span v-if="childComment.parentId != null" style="margin-left: 5px">{{
                                childComment.parentUser.nickname
                        }}</span>
                        <span style="color: #9590a6; margin-left: 5px">{{ childComment.createTime }}</span>
                    </div>
                    <div class="comment-text">
                        {{ childComment.text }}
                        <div style="margin-top: 7px">
                            <el-button type="primary" @click="likeComment(
                                childComment.commentId,
                                parentIndex,
                                index,
                                childComment.user.userId,
                                childComment.text
                            )" :class="{ liked: childComment.isLike == 1 }" size="small" plain>
                                <el-icon>
                                    <caret-top />
                                </el-icon>赞同{{ childComment.likeNum }}
                            </el-button>
                            <el-button type="primary" 
                                @click="disLikeComment(childComment.commentId, parentIndex, index)"
                                :class="{ liked: childComment.isLike == 0 }" size="small" plain>
                                <el-icon>
                                    <caret-bottom />
                                </el-icon>
                            </el-button>
                            <el-button style="border: 0"
                                @click="replay(childComment.userId, childComment.user.nickname)" size="small">
                                <el-icon>
                                    <chat-dot-round />
                                </el-icon>回复
                            </el-button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="createComment">
            <el-input v-model="replayComment.text" ref="comment" @blur.capture="splitText()"
                style="width: 88%; margin-right: 2%" :placeholder="replayName" />
            <el-button type="primary" size="small" @click="submitComment()">评论</el-button>
        </div>

        <el-pagination v-model:currentPage="currentPage" v-model:page-size="pageSize" :page-sizes="[5, 10, 20, 30, 1]"
            :small="true" :disabled="disabled" :background="background" layout="total,sizes, prev, pager, next, jumper"
            :total="total" @size-change="handleSizeChange" @current-change="handleCurrentChange" />
    </el-card>
</template>

<script>
import {CaretBottom, CaretTop, ChatDotRound, Sort} from "@element-plus/icons-vue";

export default {
  components: {ChatDotRound, CaretBottom, CaretTop, Sort},
    props: ["AnswerId", "DynamicId", "commentCount", "UserId"],
    data() {
        return {
            currentPage: 1,
            pageSize: 10,
            total: "",
            disabled: false,
            background: true,
            commentPage: "",
            replayComment: {
                userId: "",
                parentId: "",
                answerId: "",
                dynamicId: "",
                text: "",
            },
            replayName: "发个评论呗",
            webSocket: "",
            userMessage: {
                sign: "",
                userId: "",
                nickname: "",
                message: "",
                acceptUserId: "",
            },
            userLike: {
                userId: "",
                commentId: "",
                isLike: "",
            },

        };
    },
    created() {
        this.getComment();

        if (this.global.checkUserLogin()) {
            this.webSocket = this.global.initWebsocket();
        }

    },
    methods: {
        //指定评论要回复的人，未指定则评论的是本课程
        replay(parentId, name) {
            this.$nextTick(() => {
                this.$refs.comment.focus();
            });
            this.replayComment.parentId = parentId;
            this.replayName = "@" + name;
        },
        // 移除焦点后清空内容
        splitText() {
            this.replayName = "发个评论呗";
            setTimeout(() => {
                this.replayComment.parentId = "";
            }, 500);

        },

        commentMessage(userId) {
            if (!this.global.checkUserLogin()) {
                this.$message.err("请先登录");
                return;
            }
            if (this.replayComment.parentId == "") {
                this.userMessage.sign = "评论了你";
                this.userMessage.acceptUserId = this.UserId;
            } else {
                this.userMessage.sign = "回复了你";
                this.userMessage.acceptUserId = userId;
            }

            this.userMessage.userId = this.global.user.userId;
            this.userMessage.nickname = this.global.user.nickname;
            this.userMessage.message = this.replayComment.text;
            this.send(this.userMessage);
        },
        send(msg) {
            this.webSocket.send(JSON.stringify(msg));
        },
        //提交评论
        submitComment() {
            if (!this.global.checkUserLogin()) {
                this.$message.error("请先登录");
                return;
            }
            if (this.replayComment.text == "") {
                this.$message.error("评论内容不能为空");
                return;
            }
            this.replayComment.userId = this.global.user.userId;
            if (this.AnswerId != undefined) {
                this.replayComment.answerId = this.AnswerId;
            }
            if (this.DynamicId != undefined) {
                this.replayComment.dynamicId = this.DynamicId;
            }
            this.replayComment.text = this.replayComment.text.trim();
            this.axios.post("/comment/addComment", this.replayComment).then(res => {
                if (res.data.code == 200) {
                    this.$message.success("评论成功");
                    this.getComment();
                    this.commentMessage(this.replayComment.parentId);
                    this.replayComment.text = "";
                } else {
                    this.$message("评论失败");
                }
            })

        },
        handleSizeChange(val) {
            console.log(`每页 ${val} 条`);
            this.getComment();
        },
        handleCurrentChange(val) {
            console.log(`当前页: ${val}`);
            this.getComment();
        },
        getComment() {
            if (this.AnswerId != undefined) {
                this.getReplayComment(this.AnswerId);
            } else if (this.DynamicId != undefined) {
                this.getDynamicComment(this.DynamicId);
            }
        },
        getReplayComment(answerId) {
            this.axios
                .get("/comment/getAnswerComment", {
                    params: {
                        current: this.currentPage,
                        size: this.pageSize,
                        answerId: answerId,
                    },
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.commentPage = res.data.data;
                        this.total = res.data.total;
                    }
                });
        },
        getDynamicComment(dynamicId) {
            this.axios
                .get("/comment/getDynamicComment", {
                    params: {
                        current: this.currentPage,
                        size: this.pageSize,
                        dynamicId: dynamicId,
                    },
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.commentPage = res.data.data;
                        this.total = res.data.data.total;
                        console.log(this.commentPage)
                    }
                });
        },
        //移除焦点
        handleClick(event) {
            let target = event.target;
            if (target.nodeName == "SPAN" || target.nodeName == "I") {
                target = event.target.parentNode;
            }
            target.blur();
        },
        //点赞
        likeComment(commentId, parentIndex, index, acceptUserId, text) {
            if (!this.global.checkUserLogin()) {
                this.$message.error("请先登录");
                return;
            }
            console.log(commentId + "::" + parentIndex + "::" + index);
            if (parentIndex == null) {
                console.log(this.commentPage.records[index]);
                if (this.commentPage.records[index].isLike == 1) {    //根评论点过赞的情况
                    this.commentPage.records[index].isLike = 2;
                    this.userLike.isLike = 2;
                    this.commentPage.records[index].likeNum
                        = this.commentPage.records[index].likeNum - 1;
                } else {                                              //根评论没点过赞的情况
                    this.commentPage.records[index].isLike = 1;
                    this.userLike.isLike = 1;
                    this.commentPage.records[index].likeNum
                        = this.commentPage.records[index].likeNum + 1;
                }
            } else {
                if (this.commentPage.records[parentIndex].childComments[index].isLike == 1) {  //子评论点过赞的情况
                    this.commentPage.records[parentIndex].childComments[index].isLike = 2;
                    this.userLike.isLike = 2;
                    this.commentPage.records[parentIndex].childComments[index].likeNum
                        = this.commentPage.records[parentIndex].childComments[index].likeNum - 1;
                } else {                                                                       //子评论没点过赞的情况
                    this.commentPage.records[parentIndex].childComments[index].isLike = 1;
                    this.userLike.isLike = 1;
                    this.commentPage.records[parentIndex].childComments[index].likeNum
                        = this.commentPage.records[parentIndex].childComments[index].likeNum + 1;
                }
            }

            this.userLike.userId = this.global.user.userId;
            this.userLike.commentId = commentId;

            this.axios
                .post("/userLike/addLike", this.userLike)
                .then((res) => {
                    if (res.data.code == 200) {
                        this.$message.success(res.data.msg);

                        if (this.liked == 1) {
                            const userMessage = {
                                userId: this.global.user.userId,
                                acceptUserId: acceptUserId,
                                sign: "赞了你的评论",
                                message: text
                            }
                            this.axios.post('/userMessage/addUserMessage', userMessage)
                        }

                    } else {
                        this.$message.error(res.data.msg);
                    }
                });
        },
        //点踩
        disLikeComment(commentId, parentIndex, index) {
            if (!this.global.checkUserLogin()) {
                this.$message.error("请先登录");
                return;
            }
            if (parentIndex == null) {
                if (this.commentPage.records[index].isLike = 0) {          //根评论点过踩的情况
                    this.commentPage.records[index].isLike = 2;
                    this.userLike.isLike = 2;
                } else if (this.commentPage.records[index].isLike = 1) {     //根评论没点过踩，点过赞的情况
                    this.commentPage.records[index].isLike = 0;
                    this.userLike.isLike = 0;
                    this.commentPage.records[index].likeNum--;
                } else {                                                      //根评论没点过赞，没点过踩的情况
                    this.commentPage.records[index].isLike = 0;
                    this.userLike.isLike = 0;
                }
            } else {
                if (this.commentPage.records[parentIndex].childComments[index].isLike = 0) {
                    this.commentPage.records[parentIndex].childComments[index].isLike = 2;
                    this.userLike.isLike = 2;
                } else if (this.commentPage.records[parentIndex].childComments[index].isLike = 1) {
                    this.commentPage.records[parentIndex].childComments[index].isLike = 0;
                    this.userLike.isLike = 0;
                    this.commentPage.records[parentIndex].childComments[index].likeNum--;
                } else {
                    this.commentPage.records[parentIndex].childComments[index].isLike = 0;
                    this.userLike.isLike = 0;
                }
            }
            this.userLike.userId = this.global.user.userId;
            this.userLike.commentId = commentId;
            this.userLike.isLike = 0;
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
    },
};
</script>

<style scoped>
.box-card {
    margin-top: 10px;
}

.comment-sort {
    float: right;
    display: flex;
    align-items: center;
    color: #9590a6;
}

.comment-user {
    display: flex;
    align-items: center;
    font-size: 13px;
    margin-bottom: 5px;
}

.user-name {
    margin-left: 10px;
}

.comment-text {
    margin-left: 34px;
}

.comment-body {
    margin-bottom: 20px;
}

.comment-body-child {
    background: #f0f0f0;
    margin-left: 34px;
    padding-top: 5px;
    padding-left: 5px;
    padding-bottom: 5px;
}

.comment-child-item {
    margin-bottom: 5px;
}

.createComment {
    margin-bottom: 10px;
}

.el-button:focus {
    border: none;
}

.liked {
    color: #ffffff;
    background-color: #409eff;
}
</style>