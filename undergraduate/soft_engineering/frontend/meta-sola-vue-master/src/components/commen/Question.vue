<template>
    <el-card class="top-card" shadow="never">
        <h4>{{ question.problem }}</h4>
        <p class="question-describe p-set">
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ question.describe }}
        </p>
        <div style="margin-top: 7px">
            <el-button type="primary" size="small" plain>关注问题</el-button>
            <el-button type="primary" size="small" plain @click="this.$GRouter.goWriteReplay(question.questionId)">
                <el-icon>
                    <edit-pen />
                </el-icon>写回答
            </el-button>
            <el-button type="primary" size="small" @click="showInvitationDialog()" plain>
                <el-icon>
                    <circle-plus />
                </el-icon>邀请回答
            </el-button>
            <Invitation @closeInvitation="closeInvitationDialog" :invitationDialogVisible="invitationDialogVisible"
                :problem="question.problem" />
            <el-button style="border: 0;margin-left:12px" size="small">
                <el-icon>
                    <promotion />
                </el-icon>分享
            </el-button>
        </div>
    </el-card>
</template>

<script>
import Invitation from "./Invitation";
export default {
    components: {
        Invitation,
    },
    props: ["question"],
    data() {
        return {
            invitationDialogVisible: false,
        };
    },
    created() {
    },
    methods: {
        showInvitationDialog() {
            this.invitationDialogVisible = true;
        },
        closeInvitationDialog(data) {
            this.invitationDialogVisible = false;
        }
    }


}
</script>

<style scoped>
h4 {
    margin: 0;
    margin-bottom: 10px;
}

.p-set {
    margin: 0;
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    word-wrap: break-word;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    line-height: 20px;
}

.replay {
    width: 100%;
    height: 90%;
}

.top-card {
    width: 100%;
}

::v-deep .el-card__body {
    padding: 10px;
}

::v-deep .el-card {
    border: 0;
}
</style>