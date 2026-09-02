
<template>
    <div style="margin: 0 auto">
        <el-table
                :data="tableData"
                border
                style="width: 100%">
            <el-table-column
                    fixed
                    prop="log"
                    label="文物系统日志"
                    width="600">
            </el-table-column>
            <el-table-column
                    prop="dates"
                    label="时间"
                    width="120">
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
            page(currentPage){
                const _this = this;
                axios.get("http://localhost:8181/Log/findall/"+(currentPage-1)+"/5").then(function (resp) {
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
            axios.get("http://localhost:8181/Log/findall/0/5").then(function (resp) {
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