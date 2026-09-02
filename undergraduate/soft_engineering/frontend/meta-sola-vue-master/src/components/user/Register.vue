<template>
    <el-dialog v-model="registerDialogVisible" title="注册" width="40%" :before-close="handleClose">
        <el-form ref="ruleFormRef" style="padding-bottom: 10px" :model="ruleForm" :rules="rules">
            <el-form-item prop="nickname">
                <el-input v-model="ruleForm.nickname" placeholder="请输入个性签名" clearable maxlength="12" />
            </el-form-item>
            <el-form-item prop="username">
                <el-input v-model="ruleForm.username" placeholder="请输入用户名" clearable maxlength="12" />
            </el-form-item>

            <el-form-item prop="password">
                <el-input v-model="ruleForm.password" type="password" placeholder="请输入密码" maxlength="15" clearable />
            </el-form-item>
            <el-form-item prop="password0">
                <el-input v-model="ruleForm.password0" type="password" placeholder="确认密码" maxlength="15" clearable
                    @blur="checkPassword" />
            </el-form-item>
            <el-form-item prop="email">
                <el-input v-model="ruleForm.email" placeholder="请输入邮箱" clearable />
            </el-form-item>

            <el-form-item prop="picture">
                <el-upload class="avatar-uploader" :show-file-list="false" :auto-upload="true" :headers="headers"
                    action="http://localhost:8080/user/uploadImg" :on-success="handleVideoSuccess" :name="'file'">
                    <span>头像：</span>
                    <img v-if="ruleForm.picture" :src="this.global.picIp + ruleForm.picture" class="avatar" />
                    <el-icon v-else class="avatar-uploader-icon">
                        <Plus />
                    </el-icon>
                </el-upload>
            </el-form-item>
            <el-form-item class="register-fotter">
                <el-button type="primary" @click="submitForm('ruleFormRef')">注册</el-button>
                <el-button @click="closeRegister(2)">返回</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>

<script>
export default {
    props: ["registerDialogVisible"],
    setup(props, { emit }) {
        //分解context对象取出emit
        function closeRegister(data) {
            emit("closeRegister", data == null ? 0 : data);
        }
        return {
            closeRegister,
        };
    },
    data() {
        const checkUsername = (rule, value, callback) => {
            if (!value) {
                return callback(new Error("请输入用户名"));
            }
            if (value.length < 6 || value.length > 12) {
                return callback(new Error("用户名长度在 6 到 12 个字符"));
            }
            if (!/^[a-zA-Z0-9_]+$/.test(value)) {
                return callback(new Error("用户名只能是数字、字母、下划线"));
            }
            this.axios.get("/user/checkUsername?username=" + value).then((res) => {
                if (res.data.code == 500) {
                    callback(new Error("用户名已存在"));
                } else {
                    callback();
                }
            });
        };
        const checkPassword = (rule, value, callback) => {
            if (value === "") {
                callback(new Error("请输入确认密码"));
            } else if (this.ruleForm.password !== value) {
                callback(new Error("两次输入密码不一致!"));
            } else {
                callback();
            }
        };
        const checkEmail = (rule, value, callback) => {
            if (!value) {
                return callback(new Error("请输入邮箱"));
            }
            if (
                !/^[A-Za-z\d]+([-_.][A-Za-z\d]+)*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}$/.test(
                    value
                )
            ) {
                return callback(new Error("邮箱格式不正确"));
            }
            this.axios.get("/user/checkEmail?email=" + value).then((res) => {
                if (res.data.code == 500) {
                    callback(new Error("邮箱已存在"));
                } else {
                    callback();
                }
            });
        };
        return {
            headers: {
                "ip": sessionStorage.getItem("ip")
            },
            ruleForm: {
                nickname: "",
                username: "",
                password: "",
                password0: "",
                email: "",
                picture: "",
            },

            rules: {
                nickname: [
                    { required: true, message: "请输入个性签名", trigger: "blur" },
                ],
                username: [
                    { required: true, validator: checkUsername, trigger: "blur" },
                    {
                        min: 1,
                        max: 12,
                        message: "长度在 1 到 12 个字符",
                        trigger: "blur",
                    },
                ],
                password: [
                    { required: true, message: "请输入密码", trigger: "blur" },
                    {
                        min: 6,
                        max: 15,
                        message: "长度在 6 到 15 个字符",
                        trigger: "blur",
                    },
                ],
                password0: [
                    { required: true, validator: checkPassword, trigger: "blur" },
                    {
                        min: 6,
                        max: 15,
                        message: "长度在 6 到 15 个字符",
                        trigger: "blur",
                    },
                ],
                email: [
                    { required: true, validator: checkEmail, trigger: "blur" },
                    { type: "email", message: "请输入正确的邮箱", trigger: "blur" },
                ],
            },
        };
    },
    created() { },
    methods: {
        handleVideoSuccess(res, file) {
            if (res.code == 200) {
                this.ruleForm.picture = res.msg;
            }
        },
        submitForm(ruleFormRef) {
            this.$refs[ruleFormRef].validate((valid) => {
                if (valid) {
                    this.axios
                        .post("/user/register", this.ruleForm)
                        .then((res) => {
                            if (res.data.code === 200) {
                                this.$message({
                                    type: "success",
                                    message: res.data.msg,
                                });
                                this.resetForm();
                                this.closeRegister();
                            } else {
                                this.$message({
                                    type: "error",
                                    message: res.data.msg,
                                });
                            }
                        })
                        .catch((err) => {
                            console.log(err);
                        });
                } else {
                    this.$message.error("注册失败");
                }
            });
        },
        //清空ruleForm
        resetForm() {
            this.ruleForm.nickname = "";
            this.ruleForm.username = "";
            this.ruleForm.password = "";
            this.ruleForm.password0 = "";
            this.ruleForm.email = "";
            this.ruleForm.picture = "";
        },
    },
    mounted() { },
};
</script>


<style scoped>
.avatar-uploader .avatar {
    width: 60px;
    height: 60px;
    display: block;
}

::v-deep .register-fotter .el-form-item__content {
    display: inline-block !important;
    text-align: right !important;
}

::v-deep .el-upload.el-upload--text {
    height: 60px;
}
</style>
<style>
.avatar-uploader .el-upload {
    border: 1px dashed var(--el-border-color);
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
    border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 60px;
    height: 60px;
    text-align: center;
}
</style>