<template>
  <el-row class="replay-row-top">
    <div class="title">
      <el-input
        v-model="dynamic.title"
        placeholder="请输入你的标题"
        clearable
        maxlength="30"
        show-word-limit
        class="create-question"
        style="width: 100%"
        aria-required="true"
      />
    </div>

    <md-editor
      v-model="dynamic.text"
      placeholder="请输入你的动态内容"
      @onHtmlChanged="change(text)"
      @onUploadImg="uploadImg"
      :toolbarsExclude="toolbarsExclude"
    />

    <el-dialog
      v-model="submitDialogVisible"
      width="30%"
      :before-close="handleClose"
    >
      <div>
        <div>
          <el-radio v-model="dynamic.enableComment" label="1" size="large"
            >开启评论</el-radio
          >
          <el-radio v-model="dynamic.enableComment" label="0" size="large"
            >关闭评论</el-radio
          >
        </div>
        <div style="margin: 5px 0" />
        <div>
          <el-radio v-model="dynamic.enableRewward" label="1" size="large"
            >开启打赏</el-radio
          >
          <el-radio v-model="dynamic.enableRewward" label="0" size="large"
            >关闭打赏</el-radio
          >
        </div>
        <div style="margin: 5px 0" />
        <div>
          <el-radio v-model="enableShare" label="1" size="large"
            >推送给关注的人</el-radio
          >
          <el-radio v-model="enableShare" label="0" size="large"
            >不推送给关注的人</el-radio
          >
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="submitDynamic" type="primary">发布</el-button>
          <el-button @click="submitDialogVisible = false">返回</el-button>
        </span>
      </template>
    </el-dialog>
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
      toolbarsExclude: ["github", "fullscreen", "prettier"], // 工具栏排除github
      submitDialogVisible: false, // 提交回答弹窗
      enableShare: "1", //是否分享
      dynamic: {
        title: "",
        text: "",
        userId: "",
        enableComment: "1", //是否允许评论
        enableRewward: "1", //是否允许打赏
      },
      submitTime: "",
    };
  },
  methods: {
    change(text) {
      console.log(this.dynamic.text);
    },
    submitDynamic() {
     
      if (!this.global.checkUserLogin()) {
        this.$message.error("请先登录");
        return;
      }
      if (new Date().getTime() - this.submitTime < 10000) {
        this.$message.error("请勿重复提交");
        return;
      }
      this.dynamic.userId = this.global.user.userId;
      console.log(this.dynamic);
      this.axios
        .post("/dynamic/addDynamic", this.dynamic)
        .then((res) => {
          if (res.data.code == 200) {
            this.$message.success("发布成功");
            this.submitDialogVisible = false;
            this.submitTime = new Date().getTime();
          } else {
            this.$message.error(res.data.msg);
          }
        })
        .catch((err) => {
          this.$message.error("网络错误");
        });
    },
    uploadImg(fileList) {
        console.log(fileList);
        const param = new FormData();
            param.append("file",fileList[0]);
        this.axios
            .post("/user/uploadImg", param, {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            })
            .then((res) => {
            if (res.data.code == 200) {
                console.log(res.data);
                this.dynamic.text += `![](${this.global.picIp+res.data.msg})`;
            } else {
                this.$message.error(res.data.msg);
            }
            })
            .catch((err) => {
            this.$message.error("网络错误");
            });
        
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
  },
};
</script>

<style scoped>
.replay-row-top {
  padding: 0 10px;
  height: 100%;
}
::v-deep .md-toolbar-wrapper .md-toolbar {
  justify-content: normal !important;
}
::v-deep .el-card {
  border: 0;
}
.title {
  width: 100%;
  height: 50px;
  line-height: 50px;
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 30px 0;
}
</style> 