<template>
    <el-row class="row-top">
        <el-scrollbar style="width: 100%">
            <div class="scrollbar-demo-item">
                <el-card class="top">
                    <el-col :span="8" style="height: 100%;">
                        <div class="user-information">
                            <img style="height:100%" :src="this.global.picIp + user.picture" alt="" />
                        </div>

                    </el-col>
                    <el-col :span="16" style="height: 100%;width: 100%;">
                        <el-descriptions class="margin-top" title="个人资料" :column="3" :size="size" :style="blockMargin">
                            <template #extra>
                                <el-button @click="this.$GRouter.goUserInfo()"
                                    v-if="user.userId == this.global.user.userId" type="primary">编辑</el-button>
                                <el-button @click="followOtherUser(user.userId)" v-else type="primary"><span
                                        v-if="user.isFollow">已</span>关注</el-button>
                            </template>
                            <el-descriptions-item label="个性签名:">{{ user.nickname }}</el-descriptions-item>
                            <el-descriptions-item label="性别:">{{ user.sex != null ? user.sex : "未知" }}
                            </el-descriptions-item>
                            <el-descriptions-item label="邮箱:">{{ user.email }}</el-descriptions-item>
                            <el-descriptions-item label="简介:">{{ user.identity }}</el-descriptions-item>
                        </el-descriptions>
                    </el-col>

                </el-card>
                <el-card class="down">
                    <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal"
                        @select="handleSelect">
                        <el-menu-item v-for="menu in menus" :index="menu.index">{{ menu.title }}</el-menu-item>
                    </el-menu>
                    <div class="menu-context">
                        <div v-if="activeIndex == 1" class="question">
                            <div v-for="question in questions.records" class="main">
                                <h3>{{ question.problem }}</h3>
                                <div class="question-info">
                                    <span>{{ question.creaTime }}</span>
                                    <span>{{ question.answerCount }}个回答</span>
                                    <span>{{ question.followNum }}个关注</span>
                                </div>
                            </div>
                        </div>
                        <div v-else-if="activeIndex == 2" class="answer">
                            <div v-for="answer in answers.records">
                                <h3 style="margin-bottom:15px">{{ answer.question.problem }}</h3>
                                <ReplayOne class="main" :answer="answer" />
                            </div>

                        </div>
                        <div v-else-if="activeIndex == 3" class="dynamic">
                            <DynamicOne class="main" v-for="dynamic in dynamics.records" :dynamic="dynamic" />
                        </div>
                        <div v-else-if="activeIndex == 4" class="follow-user">
                            <UserOne class="main" v-for="followUser in followUsers.records"
                                :user="followUser.followUser" />
                        </div>
                        <div v-else-if="activeIndex == 5" class="follow-user">
                            <UserOne class="main" v-for="followUser in fans.records" :user="followUser.user" />
                        </div>
                        <div v-else-if="activeIndex == 6" class="collection">
                            <div class="main" v-for="collection in collections">
                                <DynamicOne v-if="collection.dynamic != null" :dynamic="collection.dynamic" />
                                <div v-else="collection.answer!=null">
                                    <h3 style="margin-bottom:15px">{{ collection.answer.question.problem }}</h3>
                                    <ReplayOne :answer="collection.answer" />
                                </div>

                            </div>
                        </div>
                    </div>
                </el-card>
            </div>
        </el-scrollbar>
    </el-row>
</template>
<script>
import MdEditor from "md-editor-v3";
import "md-editor-v3/lib/style.css";
import ReplayOne from "../commen/ReplayOne.vue";
import DynamicOne from "../commen/DynamicOne.vue";
import UserOne from "../commen/UserOne.vue";
export default {
    components: {
        MdEditor,
        ReplayOne,
        DynamicOne,
        UserOne
    },
    data() {
        return {
            user: "",
            activeIndex: '1',
            menus: [{
                index: '1',
                title: '提问',
            }, {
                index: '2',
                title: '回答',
            }, {
                index: '3',
                title: '文章',
            }, {
                index: '4',
                title: '关注',
            }, {
                index: '5',
                title: '粉丝',
            }, {
                index: '6',
                title: '收藏',
            }],
            questions: "",
            dynamics: "",
            answers: "",
            followUsers: "",
            fans: "",
            collections: "",

        }
    },
    created() {
        var userId = this.$route.params.value;
        if (this.global.checkUserLogin()) {
            this.getCollectionsByUserId(userId);
            this.getQuestionsByUserId(userId);
            this.getAnswersByUserId(userId);
            this.getFollowUsers(userId);
            this.getFans(userId);
            this.getDynamicsByUserId(userId);
        }
        this.getUser(userId);

    },
    methods: {
        getUser(userId) {
            if (userId == this.global.user.userId) {
                this.user = this.global.user;
                return;
            }
            this.axios.get("/user/getUserByUserId", {
                params: {
                    userId: userId
                }
            }).then(res => {
                if (res.data.code === 200) {
                    this.user = res.data.user;
                    console.log(this.user);
                }
            })
        },
        handleSelect(index) {
            this.activeIndex = index;
            console.log(index);
        },
        getQuestionsByUserId(userId) {
            this.axios.get("/question/getQuestionsByUserId", {
                params: {
                    userId: userId,
                    page: 1,
                    size: 10
                }
            }).then(res => {
                if (res.data.code == 200) {
                    this.questions = res.data.data;
                }
            }).catch(err => {
                console.log(err);
            })
        },
        getDynamicsByUserId(userId) {
            this.axios
                .get("/dynamic/getDynamicsByUserId", {
                    params: {
                        userId: userId,
                        page: 1,
                        size: 10
                    }
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.dynamics = res.data.data;
                    }
                });
        },
        getAnswersByUserId(userId) {
            this.axios
                .get("/answer/getAnswersByUserId", {
                    params: {
                        userId: userId,
                        page: 1,
                        size: 10
                    }
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.answers = res.data.data;
                    }
                });
        },
        getFollowUsers(userId) {
            this.axios
                .get("/userFollow/getFollowUsers", {
                    params: {
                        userId: userId,
                        page: 1,
                        size: 10
                    }
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.followUsers = res.data.data;
                    }
                });
        },
        getFans(userId) {
            this.axios
                .get("/userFollow/getFans", {
                    params: {
                        userId: userId,
                        page: 1,
                        size: 10
                    }
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.fans = res.data.data;
                    }
                });
        },
        getCollectionsByUserId(userId) {
            this.axios
                .get("/userCollection/getUserCollectionPage", {
                    params: {
                        userId: userId,
                        current: 1,
                        size: 10,
                    }
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.collections = res.data.data.records;
                    }
                });
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
    watch: {
        $route(to, from) {
            var userId = to.params.value;
            this.getCollectionsByUserId(userId);
            this.getQuestionsByUserId(userId);
            this.getAnswersByUserId(userId);
            this.getFollowUsers(userId);
            this.getFans(userId);
            this.getDynamicsByUserId(userId);
            this.getUser(userId);
        }
    }

}
</script>
<style scoped>
::v-deep .el-card__body {
    padding: 0;
    height: 100%;
}



.scrollbar-demo-item {
    align-items: center;
    justify-content: center;
    margin: 10px;
    border-radius: 4px;
}

.top {
    margin: 10px 0;
    height: 200px;
    overflow: hidden;
}

.user-information {
    height: 96%;
    width: 96%;
    margin: 2%;
}

.user-information img {
    width: 100%;
    height: 100%;
}

::v-deep .el-descriptions__extra {
    margin-top: 5px;
    margin-right: 5px;
}

.main {
    margin: 5px;
    border-bottom: 1px solid #f1f1f1 !important;
}

.question-main h3 {
    margin-top: 15px;
    margin-bottom: 5px;
}

.question-info {
    color: #8a95aa;
    font-size: 14px;
    margin-bottom: 15px;
}

.question-info span {
    margin-right: 8px;
}

::v-deep .el-card {
    border: none;
}

::v-deep .el-card.is-always-shadow {
    box-shadow: none;
}

.follow-user .main {
    margin: 10px;
    display: flex;
    align-items: center;
}

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

.p-set {
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    -webkit-line-clamp: 1;
    word-wrap: break-word;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    line-height: 20px;
    cursor: pointer;
}
</style>