var $, tab, dataStr, layer, cacheStr = window.sessionStorage.getItem("cache"),
	oneLoginStr = window.sessionStorage.getItem("oneLogin");
layui.config({
	base: "/static/js/"
}).extend({
	"bodyTab": "bodyTab"
})
layui.use(['bodyTab', 'form', 'element', 'layer', 'jquery'], function() {
	var form = layui.form,
		element = layui.element;
	$ = layui.$;
	layer = parent.layer === undefined ? layui.layer : top.layer;
	tab = layui.bodyTab({
		openTabNum: "50", //最大可打开窗口数量
		// url: "/static/json/navs.json" //获取菜单json地址
		url:"/get_navs/"
	});

	//通过顶部菜单获取左侧二三级菜单   注：此处只做演示之用，实际开发中通过接口传参的方式获取导航数据
	function getData(json) {
		$.getJSON(tab.tabConfig.url, function(data) {
			if (json) {
				dataStr = data.contentManagement;
				//重新渲染左侧菜单
				tab.render();
			}
		})
	}

	// 注：此处只做演示之用，实际开发中通过接口传参的方式获取导航数据
	getData("contentManagement");

	$("body").on("click", ".layui-nav .layui-nav-item a:not('.mobileTopLevelMenus .layui-nav-item a')", function() {
		var url = $(this).data('url');
		var text = $(this).find('cite').text()
		if (url) {
			$('#iframe').attr('src', url);
			$('.main_hd h2').text(text);
			$('.layui-layout-admin').removeClass('showMenu');
			$('body').removeClass('site-mobile');
			document.getElementById("iframe").height=0;
		}
	});



	//手机设备的简单适配
	$('.site-tree-mobile').on('click', function() {
		$('body').addClass('site-mobile');
	});
	$('.site-mobile-shade').on('click', function() {
		$('body').removeClass('site-mobile');
		$('.layui-layout-admin').removeClass('showMenu');
	});

	//隐藏左侧导航
	$(".hideMenu").click(function() {
		$(".layui-layout-admin").toggleClass("showMenu");
	});

	//判断是否web端打开
	if (!/http(s*):\/\//.test(location.href)) {
		layer.alert("请先将项目部署到 localhost 下再进行访问【建议通过tomcat、webstorm、hb等方式运行，不建议通过iis方式运行】，否则部分数据将无法显示");
	} else { //判断是否处于锁屏状态【如果关闭以后则未关闭浏览器之前不再显示】
		if (window.sessionStorage.getItem("lockcms") != "true" && window.sessionStorage.getItem("showNotice") != "true") {

		}
	};
	//判断是否设置过头像，如果设置过则修改顶部、左侧和个人资料中的头像，否则使用黑灰头像
	if (window.sessionStorage.getItem('userFace') && $(".userAvatar").length > 0) {
		var avatar = window.sessionStorage.getItem('userFace')
		$("#userFace").attr("src", avatar);
		$(".userAvatar").attr("src", avatar);
	} else {
		$("#userFace").attr("src", "../../images/face.jpg");
	}


	//退出
	$(".signOut").click(function() {
		window.sessionStorage.removeItem("menu");
		menu = [];
		window.sessionStorage.removeItem("curmenu");
	});


	//清除缓存
	$(".clearSession").click(function() {
		window.sessionStorage.clear();
		window.localStorage.clear();
		var index = layer.msg('清除缓存中，请稍候', {
			icon: 16,
			time: false,
			shade: 0.8
		});
		setTimeout(function() {
			layer.close(index);
			layer.msg("缓存清除成功！");
			setTimeout(function() {
				window.location.reload()
			}, 1000)
		}, 1000);
	})


	//	窗口滚动事件
	$(window).bind('scroll', function() {
		if ($(window).scrollTop() > 150) {
			$('.back-to-top').fadeIn();
		} else {
			$('.back-to-top').fadeOut();
		}
	});
	//返回顶部
	$('.back-to-top').click(function() {
		$('body,html').animate({
			scrollTop: 0
		}, 500);
	});




});


//iframe 自适应内容高度
function reinitIframe() {
	var iframe = document.getElementById("iframe");
	try {
		var bHeight = iframe.contentWindow.document.body.scrollHeight;
		var dHeight = iframe.contentWindow.document.documentElement.scrollHeight;
		var height = Math.max(bHeight, dHeight);
		iframe.height = height;
	} catch (ex) {}
}

window.setInterval("reinitIframe()", 600);

window.onresize = function() {
	reinitIframe();
}
