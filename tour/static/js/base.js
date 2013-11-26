/*-------------------------------------------------
     MZ Namespace
-------------------------------------------------*/
var MZ = window.MZ || {};
MZ.namespace = function() {
	var a = arguments,
		o = null,
		i, j, d;
	for (i = 0; i < a.length; ++i) {
		d = a[i].split('.');
		o = MZ;
		for (j = (d[0] === 'MZ') ? 1 : 0; j < d.length; ++j) {
			o[d[j]] = o[d[j]] || {};
			o = o[d[j]];
		}
	}
	return o;
};

MZ.namespace('util');
MZ.namespace('Cookie');
/*-------------------------------------------------
     MZ Utils
-------------------------------------------------*/
MZ.util = {
	// 数组去重
	uniqArray: function(arr) {
		var a = [],
			o = {}, i, v,
			len = arr.length;
		if (len < 2) {
			return arr;
		}
		for (i = 0; i < len; i++) {
			v = arr[i];
			if (o[v] !== 1) {
				a.push(v);
				o[v] = 1;
			}
		}
		return a;
	},
	// 浏览器是否支持地理地位
	isGeolocationSupported: function() {
		return navigator.geolocation ? true : false;
	},
	// 浏览器是否支持本地存储
	isLocalStorageSupported: function() {
		try {
			return 'localStorage' in window && window['localStorage'] !== null;
		} catch (e) {
			return false;
		}
	},
	Request: function(options, cb) {
		var defaults = {
			type: 'GET',
			url: '',
			async: true,
			data: {},
			dataType: 'json',
			timeout: 3000,
			success: function(data) {
				cb(data);
			},
			error: function(xhr, type) {
				alert('请求失败，请重新尝试!');
				//Notification.pop({
				//	'text': '请求失败，请重新尝试!'
				//}).flash(2000);
			}
		};
		var opt = $.extend(defaults, options);
		$.ajax(opt);
	}
};
/*-------------------------------------------------
     MZ Cookies(get && set)
-------------------------------------------------*/
MZ.Cookie = {
	set: function(name, value, expire, path) {
		var exp = new Date();
		exp.setTime(exp.getTime() + expire * 60 * 1000);
		document.cookie = name + "=" + encodeURIComponent(value) + ";expires=" + exp.toGMTString() + ";domain=" + document.domain.substring(1) + ";path=" + path + ";";
	},
	get: function(name) {
		var arr = document.cookie.match(new RegExp("(^| )" + name + "=([^;]*)(;|$)"));
		if (arr != null) return decodeURIComponent(arr[2]);
		return null;
	}
};
/*-------------------------------------------------
     MZ.app Namespace (for Business Code)
-------------------------------------------------*/

MZ.namespace('app');

/*------------------------------------------------
 * lazyload , extend Zepto, based on unveil.js
 * --------------------------------------------*/
(function($) {
	$.fn.unveil = function(threshold) {
		if (!this.size()) {
			return;
		}
		var $w = $(window),
			th = threshold || 0,
			retina = window.devicePixelRatio > 1,
			attrib = retina ? "data-src-retina" : "data-src",
			images = this,
			loaded,
			inview,
			source;

		this.one("unveil", function() {
			source = this.getAttribute(attrib);
			source = source || this.getAttribute("data-src");
			if (source) {
				this.setAttribute("src", source);
			}
		});

		function unveil() {
			inview = images.filter(function() {
				var $e = $(this),
					wt = $w.scrollTop(),
					wb = wt + $w.height(),
					et = $e.offset().top,
					eb = et + $e.height();

				return eb >= wt - th && et <= wb + th;
			});

			loaded = inview.trigger("unveil");
			images = images.not(loaded);
		}

		$w.scroll(unveil);
		$w.resize(unveil);
		unveil();

		return this;
	};

})(window.Zepto);

MZ.app = {

	initIndex: function() {

		function initSlider() {
			var bullets = document.getElementById('featuredMobileInd').getElementsByTagName('a');
			window.mySwipe = new Swipe(document.getElementById('slider'), {
				// startSlide: 2,
				// speed: 400,
				auto: 3000,
				continuous: false
				// disableScroll: false,
				// stopPropagation: false,
				// callback: function(index, elem) {},
				// transitionEnd: function(index, elem) {}
				,
				callback: function(pos) {
					var i = bullets.length;
					while (i--) {
						bullets[i].className = '';
					}
					bullets[pos].className = 'active';
				}
			});
		}

		// 初始化滑动
		initSlider();

	},
	sortInit: function() {
		// 初始化图片懒加载
		$('.index-list img').unveil();
	},
	detailInit: function() {
		var contTemplete = '<div class="panel panel-default" style="margin-bottom:0;">\
            <div class="panel-heading">分享<a id="J-close" href="javascript:void(0);" class="close">关闭</a></div>\
                    <div class="list-group">\
                     <a href="' + 'http://v.t.sina.com.cn/share/share.php?url=' + window.location.href + '&amp;title=智游折扣' + '" class="list-group-item" id="share-xlweibo"><i class="icon-weibo"></i>新浪微博</a>\
                     <a href="' + 'http://v.t.qq.com/share/share.php?url=' + window.location.href + '&amp;title=智游折扣' + '" class="list-group-item" id="share-txweibo"><i class="icon-qq-weibo"></i>腾讯微博</a>\
                     <a href="' + 'http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url=' + window.location.href + '&amp;title=智游折扣' + '" class="list-group-item" id="share-qqkongjian"><i class="icon-qq-zone"></i>QQ空间</a>\
            </div>\
		</div>';
		var shareBtn = $('#J-share');
		shareBtn.bind('click', function(e) {
			e.preventDefault();
			var mBox = Notification.confirm('分享', contTemplete, function(e) {
				var target = e.target;
				var _self = this;
				var targetClassName = target.className;
				if (targetClassName === 'cancel') {
					_self.hide();
				}
				if (targetClassName === 'ok') {
					_self.hide();
				}
			});
			mBox.show();
			$('#J-close').on('click', function() {
				mBox.hide();
			});
		});
	}
};