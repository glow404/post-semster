<template>
    <el-row class="row-top">
        <el-scrollbar style="width: 100%">
            <div class="scrollbar-demo-item">
                <el-form ref="ruleFormRef" :model="ruleForm" :label-position="'right'" :rules="rules"
                    label-width="120px" class="demo-ruleForm" :size="formSize" status-icon>
                    <el-form-item label="头像" prop="picture">
                        <el-upload class="avatar-uploader" :show-file-list="false" :auto-upload="true"
                            :headers="headers" action="http://localhost:8080/user/uploadImg"
                            :on-success="handleVideoSuccess" :name="'file'">
                            <img v-if="ruleForm.picture" :src="this.global.picIp + ruleForm.picture" class="avatar" />
                            <el-icon v-else class="avatar-uploader-icon">
                                <Plus />
                            </el-icon>
                        </el-upload>
                    </el-form-item>
                    <el-form-item label="个性签名" prop="nickname">
                        <el-input v-model="ruleForm.nickname" />
                    </el-form-item>
                    <el-form-item label="性别" prop="sex">
                        <el-radio-group v-model="ruleForm.sex">
                            <el-radio label="男" />
                            <el-radio label="女" />
                            <el-radio label="未知" />
                        </el-radio-group>
                    </el-form-item>
                    <el-form-item label="邮箱" prop="email">
                        <el-input v-model="ruleForm.email" />
                    </el-form-item>

                    <el-form-item label="简介" prop="inedtity">
                        <el-input v-model="ruleForm.identity" type="textarea" />
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="submitForm('ruleFormRef')">修改</el-button>
                        <el-button @click="resetForm()">重置</el-button>
                    </el-form-item>
                </el-form>
            </div>
        </el-scrollbar>
    </el-row>
</template>
<script>
export default {
    data() {
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
            callback();
        };
        return {
            formSize: 'mini',
            ruleForm: {
                userId: "",
                nickname: '',
                sex: '',
                email: '',
                identity: '',
                picture: "",
            },
            rules: {
                nickname: [
                    { required: true, message: "请输入个性签名", trigger: "blur" },
                ],
                email: [
                    { required: true, validator: checkEmail, trigger: "blur" },
                    { type: "email", message: "请输入正确的邮箱", trigger: "blur" },
                ],
            },


        }
    },
    created() {
        if (this.global.checkUserLogin()) {
            this.resetForm();
        }

    },
    methods: {
        initUserInfo() {
            this.global.user.nickname = this.ruleForm.nickname;
            this.global.user.email = this.ruleForm.email;
            this.global.user.picture = this.ruleForm.picture;
            this.global.user.sex = this.ruleForm.sex;
            this.global.user.identity = this.ruleForm.identity;
        },
        //图片回显
        handleVideoSuccess(res, file) {
            if (res.code == 200) {
                this.ruleForm.picture = res.msg;
            }
        },
        submitForm(ruleFormRef) {
            this.$refs[ruleFormRef].validate((valid) => {
                if (valid) {
                    this.axios
                        .post("/user/updateUserByUserId", this.ruleForm)
                        .then((res) => {
                            if (res.data.code === 200) {
                                this.$message({
                                    type: "success",
                                    message: res.data.msg,
                                });
                                this.getUser(this.global.user.userId)
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
                    this.$message.error("修改失败");
                }
            });
        },
        getUser(userId) {
            this.axios.get("/user/getUserByUserId", {
                params: {
                    userId: userId
                }
            }).then(res => {
                if (res.data.code === 200) {
                    //修改后的处理
                    const userInfo = res.data;
                    const oldUserInfo = JSON.parse(localStorage.getItem('userInfo'))
                    userInfo.token = oldUserInfo.token
                    localStorage.setItem("userInfo", JSON.stringify(userInfo));
                    //0.5s后执行
                    setTimeout(() => {
                        this.global.user = res.data.user;
                    }, 500);
                    
                }
            })
        },
        //重置ruleForm
        resetForm() {
            this.ruleForm.userId = this.global.user.userId;
            this.ruleForm.nickname = this.global.user.nickname;
            this.ruleForm.email = this.global.user.email;
            this.ruleForm.picture = this.global.user.picture;
            this.ruleForm.sex = this.global.user.sex;
            this.ruleForm.identity = this.global.user.identity;
        },

    },

}
</script>
<style scoped>
::v-deep .el-upload.el-upload--text {
    height: 100px;
    width: 100px;
}

.avatar {
    width: 100px;
    height: 100px;
}
</style>