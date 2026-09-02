//图片地址
const picIp = 'http://localhost:8080/img/user/';
//const picIp = 'http://4e4v608110.qicp.vip:33277/img/user/';
const uploadImg = 'http://localhost:8080/user/uploadImg';

export default {
    picIp,
    user: {
        userId: '',
        nickname: '',
        username: '',
        password: '',
        email: '',
        picture: '',
        sex: '',
        identity: '',
        level: '',
        statusId: '',
        createTime: '',
        updateTime: ''
    },
    checkUserLogin() {
        if (this.user.userId == "") {
            return false;
        } else {
            return true;
        }

    },
    loginOut() {
        if (!this.checkUserLogin) {
            return;
        }
        localStorage.removeItem('userInfo');
        this.user = {
            userId: '',
            nickname: '未登录',
            username: '',
            password: '',
            email: '',
            picture: '',
            sex: '',
            identity: '',
            level: '',
            statusId: '',
            createTime: '',
            updateTime: ''
        }
    },
    initWebsocket() {
        if (!this.checkUserLogin) {
            return "";
        }
        if ("WebSocket" in window) {
            const websocket = new WebSocket(
                "ws://localhost:8080/websocketUserMessage/" + this.user.userId
            );
            websocket.onopen = () => {
                console.log("websocket连接成功");
            };
            websocket.onmessage = (event) => {
                console.log(event.data);
            };
            websocket.onerror = (event) => {
                console.log(event.data);
            };
            websocket.onclose = (event) => {
                console.log(event.data);
            };
            return websocket;

        } else {
            console.log("浏览器不支持websocket");
        }
    },
    initWebsocketChat() {
        if (!this.checkUserLogin) {
            return "";
        }
        if ("WebSocket" in window) {
            const websocket = new WebSocket(
                "ws://localhost:8080/websocketChat/" + this.user.userId
            );
            websocket.onopen = () => {
                console.log("websocket连接成功");
            };
            websocket.onmessage = (event) => {
                console.log(event.data);
            };
            websocket.onerror = (event) => {
                console.log(event.data);
            };
            websocket.onclose = (event) => {
                console.log(event.data);
            };
            return websocket;

        } else {
            console.log("浏览器不支持websocket");
        }
    },
    //移除焦点
    handleClick(event) {
        let target = event.target;
        if (target.nodeName == "SPAN" || target.nodeName == "I") {
            target = event.target.parentNode;
        }
        target.blur();
    },
}