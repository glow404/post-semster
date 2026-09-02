<template>
    <el-card shadow="always" class="content-item content-dynamic scrollbar-demo-item">
        <div class="dynamic-user">
            <el-avatar :size="27" :src="this.global.picIp + dynamic.user.picture" />
            <span style="margin-left: 5px;margin-bottom: 3px;">{{ dynamic.user.nickname }}</span>
            <span style="margin-left: 5px; font-size: 6px; color: #9e9ea6">{{
                    dynamic.createTime
            }}</span>
        </div>
        <h4 class="dynamic-head p-set" @click="this.$GRouter.goDetailDynamic(dynamic.dynamicId)">
            {{ dynamic.title }}
        </h4>
        <p class="p-set" @click="this.$GRouter.goDetailDynamic(dynamic.dynamicId)">
            <md-editor v-model="dynamic.text" previewOnly style="max-height: 100px;" />
        </p>
        <div style="margin-top: 7px" @click="this.$GRouter.goDetailDynamic(dynamic.dynamicId)">
            <span class="m-ui" :class="{ liked: dynamic.isLike == 1 }">
                <el-icon>
                    <caret-top />
                </el-icon><span v-if="dynamic.isLike == 1">已</span>赞同{{ dynamic.likeNum }}
            </span>

            <span class="m-ui">
                <el-icon>
                    <chat-dot-round />
                </el-icon>{{ dynamic.commentCount }}条评论
            </span>
            <span class="m-ui" :class="{ liked: dynamic.isCollect }">
                <el-icon>
                    <star />
                </el-icon><span v-if="dynamic.isCollect">已</span>收藏
            </span>
        </div>
    </el-card>
</template>
<script>
import MdEditor from "md-editor-v3";
import "md-editor-v3/lib/style.css";
export default{
    props: ["dynamic"],
    components: {
        MdEditor,
    },
}
</script>
<style scoped>
.content-item {
    border: 0 !important;
}

.content-dynamic {
    height: 55% !important;
    min-height: 130px !important;
    margin-bottom: 5% !;
    /* background-color: #fff !important; */
    /*background: linear-gradient(135deg, #ffd26f, #3677ff);*/
}

.dynamic-user {
    display: flex;
    align-items: center;
}

.dynamic-head {
    height: 30%;
    max-height: 30%;
    font-size: 18px !important;
    -webkit-line-clamp: 3 !important;
    margin: 0;
    overflow: hidden;
    margin-bottom: 7px !important;
}

::v-deep .el-card__body {
    padding: 10px !important;
}

.liked {
    color: #ffffff;
    background-color: #409eff;
}
</style>