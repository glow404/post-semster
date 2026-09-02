<template>
    <el-card shadow="always" style="margin-bottom:15px">
        <div class="replay-user">
            <el-avatar :size="27" :src="this.global.picIp + answer.user.picture" />
            <span style="margin-left: 5px;margin-bottom: 3px;">{{ answer.user.nickname }}</span>
            <span style="margin-left: 5px; font-size: 6px; color: #9e9ea6">{{
                    answer.createTime
            }}</span>
        </div>
        <p class="p-set" @click="this.$GRouter.goDetailReplay(answer.answerId)">
            <md-editor v-model="answer.text" previewOnly style="max-height: 100px;" />
        </p>
        <div style="margin-top: 7px">
            <span class="m-ui">
                <el-icon>
                    <caret-top />
                </el-icon>赞同{{
                        answer.likeNum
                }}
            </span>
            <span class="m-ui">
                <el-icon>
                    <chat-dot-round />
                </el-icon>{{ answer.commentCount }}条评论
            </span>
            <span class="m-ui">
                <el-icon>
                    <star />
                </el-icon>收藏
            </span>
        </div>
    </el-card>
</template>
<script>
import MdEditor from "md-editor-v3";
import "md-editor-v3/lib/style.css";
export default{
    props: ["answer"],
    components: {
        MdEditor
    }
}
</script>
<style scopde>
.replay-user {
    display: flex;
    align-items: center;
}

::v-deep .el-card__body {
    padding: 10px !important;
}

::v-deep .el-card {
    border: 0;
}
.m-ui {
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    justify-items: center;
    background: #fff;
    color: #606266;
    border: 0;
    border-radius: 3px;
    cursor: pointer;
    margin-right: 8px;
    padding: 3px;
}
</style>