<template>
    <div>
        <el-form ref="loginForm" :model="form" :rules="rules" label-width="80px" class="login-box">
            <h3 class="login-title">中央文物局管理系统</h3>
            <el-form-item label="账号" prop="username">
                <el-input type="text" placeholder="请输入账号" v-model="form.username"/>
            </el-form-item>
            <el-form-item label="密码" prop="password">
                <el-input type="password" placeholder="请输入密码" v-model="form.password"/>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" v-on:click="onSubmit('loginForm')">登录</el-button>
                <el-button type="primary" v-on:click="reg('loginForm')">注册</el-button>
            </el-form-item>

        </el-form>

        <el-dialog
                title="温馨提示"
                :visible.sync="dialogVisible"
                width="30%"
                :before-close="handleClose">
            <span>请输入账号和密码</span>
            <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
      </span>
        </el-dialog>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                form: {
                    username: '',
                    password: ''
                },

                // 表单验证，需要在 el-form-item 元素中增加 prop 属性
                rules: {
                    username: [
                        {required: true, message: '账号不可为空', trigger: 'blur'}
                    ],
                    password: [
                        {required: true, message: '密码不可为空', trigger: 'blur'}
                    ]
                },

                // 对话框显示和隐藏
                dialogVisible: false
            }
        },
        methods: {

            onSubmit(formName) {
                const _this = this;
                // 为表单绑定验证功能
                this.$refs[formName].validate((valid) => {
                    if (valid) {
                        axios.post("http://localhost:8181/user/login",_this.form).then(function (resp) {
                            console.log(resp);
                            if (resp.data.username==_this.form.username) {
                                _this.$router.push("/Main/list");
                            }else {
                                _this.$alert("登陆失败用户名与密码不匹配","登陆失败",{
                                    confirmButtonText: '开始跳转',
                                    callback: action => {
                                        window.location.reload();
                                    }
                                })
                            }
                            // if (resp.data=="success") {
                            //     this.$router.push("/Main");
                            // }
                        });
                        // 使用 vue-router 路由到指定页面，该方式称之为编程式导航
                    } else {
                        this.dialogVisible = true;
                        return false;
                    }
                });
            },
            reg(formName){
                const _this = this;
                this.$refs[formName].validate((valid) => {
                    if (valid) {
                        axios.post("http://localhost:8181/user/reg",_this.form).then(function (resp) {
                            if (resp.data=="success") {
                                _this.$alert("注册成功","注册成功",{
                                    confirmButtonText: '开始跳转',
                                    callback: action => {
                                        _this.$router.push("/Main/list");
                                    }
                                })
                            }else {
                                _this.$alert("用户名重复或注册失败","用户名重复或注册失败",{
                                    confirmButtonText: '确定',
                                    callback: action => {
                                        window.location.reload();
                                    }
                                })
                            }
                        });
                        // 使用 vue-router 路由到指定页面，该方式称之为编程式导航
                    } else {
                        this.dialogVisible = true;
                        return false;
                    }
                });
            }
        }
    }
</script>

<style scoped>
    .login-box {
        border: 1px solid #DCDFE6;
        width: 350px;
        margin: 180px auto;
        padding: 35px 35px 15px 35px;
        border-radius: 5px;
        -webkit-border-radius: 5px;
        -moz-border-radius: 5px;
        box-shadow: 0 0 25px #909399;
    }

    .login-title {
        text-align: center;
        margin: 0 auto 40px auto;
        color: #303133;
    }
</style>