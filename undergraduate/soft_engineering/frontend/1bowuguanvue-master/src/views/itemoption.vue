<template>
    <div style="margin: 0 auto">
        <el-form :model="ruleForm" :rules="rules" ref="ruleForm" label-width="100px" class="demo-ruleForm">
            <el-form-item label="文物编号" prop="id">
                <el-input v-model="ruleForm.id" readonly=""></el-input>
            </el-form-item>
            <el-form-item label="文物名称" prop="name">
                <el-input v-model="ruleForm.name" readonly=""></el-input>
            </el-form-item>
            <el-form-item label="文物隶属" prop="belong">
                <el-input v-model="ruleForm.belong" readonly=""></el-input>
            </el-form-item>
            <el-form-item label="文物操作" prop="type">
                <el-select v-model="ruleForm.status" placeholder="请选择操作类别">
                    <el-option label="清洗" value="清洗"></el-option>
                    <el-option label="展出" value="展出"></el-option>
                    <el-option label="复刻" value="复刻"></el-option>
                    <el-option label="保养" value="保养"></el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="操作时间" required>
                <el-date-picker
                        v-model="ruleForm.date"
                        type="datetime"
                        placeholder="选择日期时间"
                        align="right"
                >
                </el-date-picker>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="submitForm('ruleForm')">提交</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                ruleForm: {
                    id:'',
                    name: '',
                    belong: '',
                    status: '',
                    date: ''
                },
                rules: {
                    name: [
                        { required: true, message: '请输入文物编号', trigger: 'blur' }
                    ],
                    belong: [
                        { required: true, message: '请输入文物隶属', trigger: 'blur' }
                    ],
                    status: [
                        { required: true, message: '请选择文物状态类别', trigger: 'change' }
                    ],
                    date: [
                        { type: 'date', required: true, message: '请选择日期', trigger: 'change' }
                    ]
                }
            };
        },
        methods: {
            submitForm(formName) {
                const _this = this;
                this.$refs[formName].validate((valid) => {
                    if (valid) {
                        axios.post('http://localhost:8181/Log/add',this.ruleForm).then(function (resp) {
                            if (resp.data == 'success'){
                                _this.$alert(_this.ruleForm.name+"事务已提交","事务已提交",{
                                        confirmButtonText: '确定',
                                        callback: action => {
                                            _this.$router.push('/Main/list')
                                        }
                                    }
                                )
                            }
                        })
                    } else {
                        console.log('error submit!!');
                        return false;
                    }
                });
            },
            resetForm(formName) {
                this.$refs[formName].resetFields();
            }
        },
        created(){
            const _this = this;
            //alert(this.$route.query.id);
            axios.get('http://localhost:8181/item/findbyid/'+this.$route.query.id).then(function (resp) {
                _this.ruleForm = resp.data;
            })
        }
    }
</script>

<style scoped>

</style>