<template>
  <el-col :span="6" class="right">
    <div class="riqi">
      <div class="yd">
        <a @click="syy(1)" style="cursor: pointer;color:#9e9e99">上一月 </a>&nbsp;&nbsp;
        {{ nowYear }}年{{ nowMonth }}月 &nbsp;&nbsp;

        <a @click="xyy(1)" style="cursor: pointer;color:#9e9e99"> 下一月</a>
      </div>
      <ul v-html="html"></ul>
      <div class="days">
        <p>您本月已累计签到：{{ signDate.length }}</p>
      </div>
    </div>
  </el-col>
</template>
<script>

export default {
  data() {
    return {
      nowYear: new Date().getFullYear(), //获取年份
      nowMonth: new Date().getMonth() + 1, //获取月份
      signDate: [1, 2, 3, 4, 6, 7, 8, 9, 15, 31], //从后台获取签到日期
      html: "", //代码块
    };
  },
  methods: {
    /*时间判断*/
    isLeap(year) {
      return year % 4 == 0
        ? year % 100 != 0
          ? 1
          : year % 400 == 0
          ? 1
          : 0
        : 0;
    },
    /*点击上一页*/
    syy(id) {
      if (this.nowMonth == 1) {
        this.nowYear = parseInt(this.nowYear) - 1;
        this.nowMonth = 12;
        this.aaa();
        return;
      }
      this.nowMonth = parseInt(this.nowMonth) - 1;
      this.aaa();
    },
    /*点击下一页*/
    xyy(id) {
      if (this.nowMonth == 12) {
        this.nowYear = parseInt(this.nowYear) + 1;
        this.nowMonth = 1;
        this.aaa();
        return;
      }
      this.nowMonth = parseInt(this.nowMonth) + 1;
      this.aaa();
    },
    /*点击当前事件考勤事件*/
    addComment: function (event) {
      if (event.target.nodeName === "P") {
        if (event.target.className === "succe") {
          alert("当天您已签到!今天是" + event.target.innerHTML + "号");
          return;
        }
        // 获取触发事件对象的属性
        console.log(event);
        console.log(event.target);
        console.log(event.target.nodeName); //获取标签
        console.log(event.target.className); //获取css
        console.log(event.target.innerHTML); //获取内容
        console.log(event.target.innerText); //获取内容
        alert("当天暂无考勤记录");
      }
    },
    /*日历方法*/
    aaa() {
      //获取当前时间
      //alert(this.nowYear+"年"+this.nowMonth)
      var days_per_month = new Array(
        31,
        28 + this.isLeap(this.nowYear),
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31
      ); //每个月的天数
      var dateHtml =
        "<li>日</li><li>一</li><li>二</li><li>三</li><li>四</li><li>五</li><li>六</li>"; //日历头部
      var s = new Date(
        this.nowYear + "/" + this.nowMonth + "/" + "01"
      ).getDay(); //获取本月的一号是星期几 0星期天
      //alert(s)
      if (s > 0);
      for (var i = s - 1; i >= 0; i--) {
        // var s=days_per_month[this.nowMonth - 1];//获取当前月份的最大天数 最后一天
        var year = parseInt(this.nowMonth) - 1; //获取当前月份
        if (year == 0) {
          year = 12;
        }
        //alert(s+"--"+parseInt(days_per_month[year-1])+"--"+i); //days_per_month[year-1] 获取上个月的天数
        var maxnowMonth = parseInt(days_per_month[year - 1]) - i;
        dateHtml +=
          "<li style='color: #9e9898;height:39.99px'>" + maxnowMonth + "</li>"; //获取上月末尾天数  补齐本月日历显示
      }

      /*循坏输出 日历访日 html中*/
      for (var j = 0; j < days_per_month[this.nowMonth - 1]; j++) {
        if (this.signDate.length >= 1) {
          //有签到历史
          for (var n = 0; n < this.signDate.length; n++) {
            if (j == this.signDate[n] - 1) {
              //判断前天数和 签到天数相同 进入 写人css区分
              var dateHtmlp = "<p class='succe' >" + (j + 1) + "</p>";
              break;
            } else {
              if (j < this.signDate[this.signDate.length - 1]) {
                dateHtmlp = "<p class='failed'>" + (j + 1) + "</p>";
              } else {
                dateHtmlp = "<p>" + (j + 1) + "</p>";
              }
            }
          }
        } else {
          dateHtmlp = "<p class='failed'>" + (j + 1) + "</p>"; // 本月每天都没有签到
        }
        dateHtml += "<li>" + dateHtmlp + "</li>";
      }

      //console.log(dateHtml);
      /* $('#rili').append(dateHtml)*/
      /*  $('#rili').html(dateHtml);*/
      this.html = dateHtml;
    },
  },
  created() {
    /*调用初始化当前考勤*/
    this.aaa();
  },
};
</script>
<style scope>
.right {
  height: 90%;
  background-color: #f1f6fc;
}
ul {
  display: block;
  list-style-type: disc;
  margin-block-start: 1em;
  margin-block-end: 1em;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
  padding-inline-start: 0px;
}
.riqi {
  width: 92%;
  margin: 10px 4%;
  height: 19em;
  margin-bottom: 10px;
  border-radius: 16px;
  background-color: #fff;
}
.riqi .yd {
  width: 92%;
  text-align: center;
  padding-left: 4%;
  padding-top: 15px;
  font-size: 15px;
  height: 2rem;
}
.riqi ul {
  margin: 0 auto;
  width: 92%;
  height: auto;
  overflow: hidden;
}
.riqi ul li {
  display: flex;
  justify-content: center;
  align-items: center;
  float: left;
  position: relative;
  width: 14%;
  height: auto;
  line-height: 0.85rem;
  text-align: center;
  font-size: 0.5em;
  color: #000;
}
.riqi ul li p {
  width: 3em;
  height: 3em;
  line-height: 3em;
  text-align: center;
  border-radius: 100%;
}
.riqi ul li p i {
  position: absolute;
  top: 0.34rem;
  left: -0.145rem;
  background: rgb(255, 255, 255);
  width: 1.68rem;
  height: 0.72rem;
  right: unset;
}
.riqi ul li p.succe {
  background: #087592;
  color: #fff;
}
.riqi ul li p.succe i {
  position: absolute;
  top: 1.46rem;
  right: -0.8rem;
  background: rgba(248, 190, 69, 1);
  width: 1.6rem;
  height: 0.48rem;
  left: unset;
}
.riqi ul li p.failed:after {
  content: "";
  color: red;
  position: absolute;
  top: -0.2rem;
  right: 0;
  font-weight: bold;
}
.riqi .days {
  font-size: 16px;
  margin: 0px 5px;
  display: flex;
  -webkit-box-pack: justify;
  -webkit-justify-content: space-between;
  -ms-flex-pack: justify;
  justify-content: space-between;
}
.riqi .days p {
  width: 100%;
  text-align: center;
  color: red;
}
.riqi .days p a {
  color: blue;
}
</style>