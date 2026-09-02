<template>
    <el-row class="replay-row-top">
        <el-scrollbar style="width: 100%">
            <div class="scrollbar-demo-item">
                <h2 style="text-align: center">{{ dynamic.title }}</h2>
                <div class="dynamic-user">
                    <el-avatar :size="27" :src="this.global.picIp + dynamic.user.picture" />
                    <span style="margin-left: 5px">{{ dynamic.user.nickname }}</span>
                    <span class="time">{{ dynamic.updateTime }}</span>
                </div>

                <md-editor v-model="dynamic.text" @onHtmlChanged="change(text)" @onUploadImg="uploadImg" previewOnly />
                <div style="margin-top: 7px">
                    <el-button type="primary" :class="{ liked: liked == 1 }" @click="likeDynamic()" plain>
                        <el-icon>
                            <caret-top />
                        </el-icon>赞同{{ dynamic.likeNum }}
                    </el-button>
                    <el-button type="primary" :class='{ liked: liked == 0 }' @click="disLikeDynamic()" plain>
                        <el-icon>
                            <caret-bottom />
                        </el-icon>
                    </el-button>
                    <el-button type="primary" @click="collectDynamic()" :class='{ liked: dynamic.isCollect }' plain>
                        <el-icon>
                            <star />
                        </el-icon>收藏
                    </el-button>
                </div>
                <Comment :DynamicId="dynamic.dynamicId" :commentCount="dynamic.commentCount"
                    :UserId="dynamic.user.userId" v-if="dynamic.enableComment == 1" />
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
            text: "```java\npublic static void main \n```\n## 1123\n# 123\n## 123\n",
            liked: 2,
            dynamicId: this.$route.params.value,
            dynamic: {
                title: "",
                user: {
                    nickname: "",
                    picture: "",
                },
                text: "",
                likeNum: "",
                commentCount: "",
            },
            userLike: {
                userId: "",
                dynamicId: this.dynamicId,
                isLike: "",
            },
        };
    },
    created() {
        this.getDynamicByDynamicId(this.dynamicId);
        this.getIsLike();
    },
    methods: {
        getDynamicByDynamicId(dynamicId) {
            this.axios
                .get("/dynamic/getDynamicByDynamicId", {
                    params: {
                        dynamicId: dynamicId,
                    },
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.dynamic = res.data.data;
                    }
                });
        },
        change(text) {
            this.text = text;
        },
        uploadImg(e) {
            console.log(e);
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
        likeDynamic() {
            if (!this.global.checkUserLogin()) {
                this.$message.error("请先登录");
                return;
            }
            //点过赞就取消赞
            if (this.liked == 1) {
                this.liked = 2;
                this.userLike.isLike = 2;
                this.dynamic.likeNum = this.dynamic.likeNum - 1;
            } else {
                this.userLike.isLike = 1;
                this.liked = 1;
                this.dynamic.likeNum = this.dynamic.likeNum + 1;
            }

            this.userLike.userId = this.global.user.userId;
            this.userLike.dynamicId = this.dynamicId;

            this.axios
                .post("/userLike/addLike", this.userLike)
                .then((res) => {
                    if (res.data.code == 200) {
                        this.$message.success(res.data.msg);

                        if (this.liked == 1) {
                            const userMessage = {
                                userId: this.global.user.userId,
                                acceptUserId: this.dynamic.dynamicId,
                                sign: "赞了你的动态",
                                message: this.dynamic.title
                            }
                            this.axios.post('/userMessage/addUserMessage', userMessage)
                        }

                    } else {
                        this.$message.error(res.data.msg);
                    }
                });
        },
        //点踩
        disLikeDynamic() {
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
                this.dynamic.likeNum = this.dynamic.likeNum - 1;
            } else {                              //没点过赞的情况
                this.liked = 0;
                this.userLike.isLike = 0;
            }

            this.userLike.userId = this.global.user.userId;
            this.userLike.dynamicId = this.dynamicId;

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
                dynamicId: this.dynamicId,
            };
            this.axios.post("/userLike/getIsLike", userLike).then((res) => {
                if (res.data.code == 200) {
                    this.liked = res.data.data;
                }
            });
        },
        //收藏
        collectDynamic() {
            if (!this.global.checkUserLogin()) {
                this.$message.error("请先登录");
                return;
            }
            const collect = {
                userId: this.global.user.userId,
                dynamicId: this.dynamicId,
            };
            if (!this.dynamic.isCollect) {
                this.dynamic.isCollect = true;
                this.axios.post("/userCollection/addUserCollection", collect).then((res) => {
                    if (res.data.code == 200) {
                        this.$message.success(res.data.msg);
                    } else {
                        this.$message.error(res.data.msg);
                    }
                });
            } else {
                this.dynamic.isCollect = false;
                this.axios.get("/userCollection/deleteUserCollectionDynamic", {
                    params: {
                        userId: this.global.user.userId,
                        dynamicId: this.dynamicId,
                    },
                }).then((res) => {
                    if (res.data.code == 200) {
                        this.$message.success(res.data.msg);
                    } else {
                        this.$message.error(res.data.msg);
                    }
                });
            }

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

.detailDynamic {
    width: 66.66666667%;
}

.time {
    margin-left: 10px;
    font-size: 10px;
    margin-top: 6px;
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

.liked {
    color: #ffffff;
    background-color: #409eff;
}
</style>