import router from ".";


export class GRouter {
    goContent() {
        router.push('/Content');
    }
    goReplay(questionId) {
        router.push('/Replay/' + questionId);
    }
    goDetailReplay(answerId) {
        router.push('/DetailReplay/' + answerId);
    }
    goWriteReplay(questionId) {
        router.push('/WriteReplay/' + questionId);
    }
    goDetailDynamic(dynamicId) {
        router.push('/DetailDynamic/' + dynamicId);
    }
    goWriteDynamic() {
        router.push('/WriteDynamic');
    }
    goChat(userId) {
        router.push('/Chat/' + userId);
    }
    goMine(userId) {
        router.push('/Mine/' + userId);
    }
    goUserInfo() {
        router.push('/UserInfo');
    }

}
const EC = new GRouter();

export default EC;