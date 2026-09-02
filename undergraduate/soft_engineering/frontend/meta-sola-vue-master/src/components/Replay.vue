<template>
    <el-row class="replay-row-top">
        <el-scrollbar style="width: 100%">
            <div class="scrollbar-demo-item">
                <Question :question="question" />
                <el-divider />
                <el-col v-if="answers.length > 0" :span="20" :offset="2">
                    <ReplayOne v-for="answer in answers" :answer="answer" />
                </el-col>
                <el-empty v-else description="暂时还没有回答" :image-size="100" />
            </div>
        </el-scrollbar>
    </el-row>
</template>

<script>
import Question from "./commen/Question";
import ReplayOne from "./commen/ReplayOne";

export default {
    components: {
    Question,
    ReplayOne,
},
    name: "Reply",
    data() {
        return {
            questionId: this.$route.params.value,
            question: "",
            answers: "",
        };
    },
    created() {
        this.getQuestionByQuestionId(this.questionId);
        this.getAnswerPageByQuestionId(this.questionId);
    },
    methods: {
        getQuestionByQuestionId(questionId) {
            this.axios
                .get("/question/getQuestionById?questionId=" + questionId)
                .then((res) => {
                    if (res.data.code == 200) {
                        this.question = res.data.data;
                    }
                });
        },
        getAnswerPageByQuestionId(questionId) {
            this.axios
                .post("/answer/getAnswerPageByQuestionId", {
                    questionId: questionId,
                    current: 1,
                    size: 10,
                })
                .then((res) => {
                    if (res.data.code == 200) {
                        this.answers = res.data.data.records;
                    }
                });
        },
    },
    mounted() {
    },
};
</script>

<style scoped>
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
::v-deep .el-card{
    border:none
}



</style>