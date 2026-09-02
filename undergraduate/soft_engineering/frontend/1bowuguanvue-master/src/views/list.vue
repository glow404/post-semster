
<template>
    <div style="margin: 0 auto">
        <el-table
                :data="tableData"
                border
                style="width: 100%">
            <el-table-column
                    fixed
                    prop="id"
                    label="文物编号"
                    width="150">
            </el-table-column>
            <el-table-column
                    fixed
                    prop="name"
                    label="文物名称"
                    width="150">
            </el-table-column>
            <el-table-column
                    prop="info"
                    label="文物介绍"
                    width="120">
            </el-table-column>
            <el-table-column
                    prop="addr"
                    label="出土地址"
                    width="120">
            </el-table-column>
            <el-table-column
                    prop="belong"
                    label="文物隶属"
                    width="120">
            </el-table-column>
            <el-table-column
                    prop="status"
                    label="文物状态"
                    width="300">
            </el-table-column>
            <el-table-column
                    prop="date"
                    label="入库时间"
                    width="180">
            </el-table-column>
            <el-table-column
                    fixed="right"
                    label="操作"
                    width="120">
                <template slot-scope="scope">
                    <el-button @click="edit(scope.row)" type="text" size="small">修改</el-button>
                    <el-button @click="option(scope.row)" type="text" size="small">操作</el-button>
                    <el-button @click="remove(scope.row)" type="text" size="small">删除</el-button>
                </template>
            </el-table-column>
        </el-table>
        <el-pagination
                       background
                       layout="prev, pager, next"
                       :total="total"
                       :page-size="pageSize"
                        @current-change="page">
        </el-pagination>
    </div>
</template>

<script>
    export default {
        methods: {
            remove(row){
                //alert(row.id);
                const _this = this;
                axios.delete('http://localhost:8181/item/remove/'+row.id).then(function (resp) {
                    _this.$alert(row.name+"删除成功","删除成功",{
                            confirmButtonText: '确定',
                            callback: action => {
                                window.location.reload();
                            }
                        }
                    )
                })
            },
            edit(row) {
                // alert(row.id);
                this.$router.push({
                    path: '/Main/updata',
                    query:{
                        id: row.id
                    }
                })
            },
            option(row){
                this.$router.push({
                    path: '/Main/itemoption',
                    query:{
                        id: row.id
                    }
                })
            },
            page(currentPage){
                const _this = this;
                axios.get("http://localhost:8181/item/findall/"+(currentPage-1)+"/5").then(function (resp) {
                    _this.tableData = resp.data.content
                    _this.pageSize = resp.data.size;
                    _this.total = resp.data.totalElements;
                })
            }
        },
        data() {
            return {
                tableData: null
            }
        },
        created() {
            const _this = this;
            axios.get("http://localhost:8181/item/findall/0/5").then(function (resp) {
                    // this.tableData = resp
                _this.tableData = resp.data.content
                _this.pageSize = resp.data.size;
                _this.total = resp.data.totalElements;
            })
        }
    };
</script>



<style scoped>

</style>