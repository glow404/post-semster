<template>
    <el-row class="content-row-top">
        <el-col :span="22" :offset="1">
            <el-carousel :interval="3000" ref="img" :autoplay="true" :initial-index="1" :loop="true" type="card"
                height="200px">
                <el-carousel-item v-for="question in questions">
                    <el-card shadow="always" class="content-item content-question">
                        <h4 class="question-text p-set" @click="this.$GRouter.goReplay(question.questionId)">
                            {{ question.problem }}
                        </h4>
                        <p class="question-describe p-set" @click="this.$GRouter.goReplay(question.questionId)">
                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ question.describe }}
                        </p>
                        <div class="question-bottom">
                            <span style="
                        font-size: 13px;
                        display: flex;
                        align-items: center;
                        float: right;
                        margin-right: 20px;
                        ">
                                <el-icon style="font-size: 15px">
                                    <chat-line-round />
                                </el-icon>{{ question.answerCount }}条回答
                            </span>
                            <span class="m-ui" :class="{ liked: question.isFollow }"><span
                                    v-if="question.isFollow">已</span>关注{{ question.followNum }}</span>
                        </div>
                    </el-card>
                </el-carousel-item>
            </el-carousel>
        </el-col>
    </el-row>
    <el-row class="content-row-down">
        <el-col :span="20" :offset="2" style="height: 300px; overflow: auto">
            <el-scrollbar>
                <DynamicOne v-for="dynamic in dynamics" :dynamic="dynamic" />
            </el-scrollbar>
        </el-col>
    </el-row>
</template>
<script>
import DynamicOne from "./commen/DynamicOne"
export default {
    name: "Index",
    components: {
    DynamicOne,
},
    data() {
        return {
            questions: "",
            dynamics: "",
        };
    },
    created() {
        this.getQuestionPage();
        this.getDynamicPage();
    },
    methods: {
        getQuestionPage() {
            this.axios
                .post("/question/getQuestionPage", {
                    current: 1,
                    size: 5,
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.questions = res.data.data.records;
                        //延迟加载
                        setTimeout(() => {
                            this.$refs.img.next();
                        }, 100);

                    }
                });
        },
        getDynamicPage() {
            this.axios
                .post("/dynamic/getDynamicPage", {
                    current: 1,
                    size: 10,
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.dynamics = res.data.data.records;
                    }
                });
        },
    },
};
</script>

<style scoped>
.el-carousel__item h3 {
    color: #475669;
    font-size: 14px;
    opacity: 0.75;
    line-height: 100%;
    height: 100%;
    margin: 0;
    text-align: center;
}

.el-carousel__item:nth-child(2n) {
    background-color: #99a9bf;
}

.el-carousel__item:nth-child(2n + 1) {
    background-color: #d3dce6;
}

/* ::v-deep
  .el-carousel__indicators.el-carousel__indicators--horizontal.el-carousel__indicators--outside {
  display: none;
}
::v-deep .el-carousel__item.is-active.is-in-stage.el-carousel__item--card {
  position: relative;
} */

::v-deep .el-carousel.el-carousel--horizontal.el-carousel--card {
    height: 100%;
}

.content {
    height: 90%;
    width: 100%;
}

.content-row-top {
    margin-top: 10px;
    height: 40%;
}

.conntent-row-down {
    height: 60%;
}

.content-item {
    border: 0 !important;
}

.content-question {
    height: 100%;
    background: linear-gradient(135deg, #17ead9, #6078ea);
}

.question-left,
.question-right {
    text-align: center;
    display: flex;
    align-items: center;
}

.question-text {
    height: 30%;
    max-height: 30%;
    font-size: 18px !important;
    -webkit-line-clamp: 4 !important;
    margin: 0;
    overflow: hidden;
}

.question-describe {
    max-height: 50%;
    margin-top: 5px !important;
}

.question-bottom {
    position: absolute;
    bottom: 10px;
    width: 100%;
}


.scrollbar-demo-item {
    align-items: center;
    justify-content: center;
    margin: 10px;
    border-radius: 4px;
}

::v-deep .el-card{
    border: 0 !important;
}

::v-deep .el-card__body {
    padding: 10px !important;
}


</style>