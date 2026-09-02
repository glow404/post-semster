<template>
    <div style="margin: 0 auto">
        <el-form :model="ruleForm" :rules="rules" ref="ruleForm" label-width="100px" class="demo-ruleForm">
            <el-form-item label="用户名" prop="username">
                <el-input v-model="ruleForm.username"></el-input>
            </el-form-item>
            <el-form-item label="原密码" prop="password">
                <el-input v-model="ruleForm.password"></el-input>
            </el-form-item>
            <el-form-item label="新密码" prop="role">
                <el-input v-model="ruleForm.role"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="submitForm('ruleForm')">提交</el-button>
                <el-button @click="resetForm('ruleForm')">重置</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                ruleForm: {
                    password: '',
                    role:'',
                    username:'',
                },
                rules: {
                    password: [
                        { required: true, message: '此处不能为空', trigger: 'blur' }
                    ],
                    role: [
                        { required: true, message: '此处不能为空', trigger: 'blur' }
                    ],
                    username: [
                        { required: true, message: '此处不能为空', trigger: 'blur' }
                    ],
                }
            };
        },
        methods: {
            submitForm(formName) {
                const _this = this;
                this.$refs[formName].validate((valid) => {
                    if (valid) {
                        //alert(this.$route.query.id);
                        axios.post('http://localhost:8181/user/updata',_this.ruleForm).then(function (resp) {
                            console.log(resp);
                            if (resp.data == 'success'){
                                _this.$alert("修改成功","修改成功",{
                                        confirmButtonText: '确定',
                                        callback: action => {
                                            _this.$router.push('/')
                                        }
                                    }
                                )
                            }else {
                                _this.$alert("修改失败","修改失败",{
                                        confirmButtonText: '确定',
                                        callback: action => {
                                            _this.$router.push('/Main/list')
                                        }
                                    }
                                )
                            }
                        })
                    } else {
                        return false;
                    }
                });
            },
            resetForm(formName) {
                this.$refs[formName].resetFields();
            }
        }
    }
</script>

<style scoped>

</style>