/**
 * Created by X on 25/11/13.
 */

var share = document.getElementById('J-share');
var share_xlweibo = document.getElementById('share-xlweibo');
var share_txweibo = document.getElementById('share-txweibo');
var share_qqkongjian = document.getElementById('share-qqkongjian');
var phone = document.getElementById('phone');
var taoyitao = document.getElementById('taoyitao');

addListener(share, 'click', function() {
  ga('send', 'event', '营销类', '转发', '分享', 1);
});

addListener(share_xlweibo, 'click', function() {
  ga('send', 'event', '营销类', '转发', '新浪微博', 1);
});

addListener(share_txweibo, 'click', function() {
  ga('send', 'event', '营销类', '转发', '腾讯微博', 1);
});

addListener(share_qqkongjian, 'click', function() {
  ga('send', 'event', '营销类', '转发', 'QQ空间', 1);
});

addListener(phone, 'click', function() {
  ga('send', 'event', '转化类', '预订', '电话预订', 1);
});

addListener(taoyitao, 'click', function() {
  ga('send', 'event', '功能类', '淘一淘', '淘一淘', 1);
});

/**
 * Utility to wrap the different behaviors between W3C-compliant browsers
 * and IE when adding event handlers.
 *
 * @param {Object} element Object on which to attach the event listener.
 * @param {string} type A string representing the event type to listen for
 *     (e.g. load, click, etc.).
 * @param {function()} callback The function that receives the notification.
 */

function addListener(element, type, callback) {
 if (element.addEventListener) element.addEventListener(type, callback);
 else if (element.attachEvent) element.attachEvent('on' + type, callback);
}