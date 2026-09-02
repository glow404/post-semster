<template>
  <el-dialog
    v-model="loginDialogVisible"
    title="登录"
    width="30%"
    :before-close="closeLogin"
  >
    <el-form
      ref="ruleFormRef"
      style="margin-top: 20px"
      :model="ruleForm"
      :rules="rules"
    >
      <el-form-item prop="username">
        <el-input
          v-model="ruleForm.username"
          placeholder="请输入你的用户名"
          clearable
          maxlength="12"
          style="width: 100%"
        />
      </el-form-item>
      <div style="margin: 5px 0" />
      <el-form-item prop="password">
        <el-input
          v-model="ruleForm.password"
          placeholder="请输入你的密码"
          maxlength="15"
          clearable
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="login('ruleFormRef')">登录</el-button>
        <el-button @click="closeLogin(2)">注册</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
export default {
  props: ["loginDialogVisible"],
  setup(props, { emit }) {
    //分解context对象取出emit
    function closeLogin(data) {
      emit("closeLogin", data == null ? 0 : data);
    }
    function loginInfo() {
      emit("loginInfo", this.user);
    }
    return {
      closeLogin,
      loginInfo,
    };
  },
  data() {
    return {
      ruleForm: {
        username: "",
        password: "",
      },
      user: "",
      rules: {
        username: [
          { required: true, message: "请输入用户名", trigger: "blur" },
          {
            min: 3,
            max: 12,
            message: "长度在 3 到 12 个字符",
            trigger: "blur",
          },
        ],
        password: [
          { required: true, message: "请输入密码", trigger: "blur" },
          {
            min: 5,
            max: 15,
            message: "长度在 5 到 15 个字符",
            trigger: "blur",
          },
        ],
      },
    };
  },
  methods: {
    //登录
    login(ruleFormRef) {
      this.$refs[ruleFormRef].validate((valid) => {
        if (valid) {
          this.axios
            .post("/user/login", {
              username: this.ruleForm.username,
              password: this.ruleForm.password,
            })
            .then((res) => {
              if (res.data.code == 200) {
                this.$message.success(res.data.msg);
                this.user = res.data.user;

                this.closeLogin();
                //将user提交给head
                this.loginInfo();
                this.ruleForm.username = "";
                this.ruleForm.password = "";
                //登录后的处理
                localStorage.setItem("userInfo", JSON.stringify(res.data));
                this.global.user=res.data.user;
                // this.global.initWebSocket();
                this.axios.defaults.headers["Authorization"] = res.data.token;
              } else {
                this.$message.error(res.data.msg);
              }
            });
        } else {
          this.$message.error("登录失败");
        }
      });
    },
  },
};
</script>

<style scoped>
</style>