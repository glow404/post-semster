<template>
    <button class="btn">
        <slot class="solt"></slot>
    </button>
</template>
<script>
export default{
}
</script>
<style scoped>
.btn{
    font-size: 12px;
    display: inline-flex;
    align-items: center;
    justify-items: center;
    background: #fff;
    color: #606266;
    border: 0;
    border-radius: 5px;
    cursor: pointer;
}
.solt{
    margin-top: 5px;
}
</style>