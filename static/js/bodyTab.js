
var tabFilter, menu = [],
	liIndex, curNav, delMenu,
	changeRefreshStr = window.sessionStorage.getItem("changeRefresh");
layui.define(["element", "jquery"], function(exports) {
	var element = layui.element,
		$ = layui.$,
		layId,
		Tab = function() {
			this.tabConfig = {
				openTabNum: undefined, //最大可打开窗口数量
				tabFilter: "bodyTab", //添加窗口的filter
				url: undefined //获取菜单json地址
			}
		};
	//生成左侧菜单
	Tab.prototype.navBar = function(strData) {
		var data;
		if (typeof(strData) == "string") {
			var data = JSON.parse(strData); //部分用户解析出来的是字符串，转换一下
		} else {
			data = strData;
		}
		var ulHtml = '';
		for (var i = 0; i < data.length; i++) {
				ulHtml += '<li class="layui-nav-item layui-nav-itemed">';
			if (data[i].children != undefined && data[i].children.length > 0) {
				ulHtml += '<a>';
				if (data[i].icon != undefined && data[i].icon != '') {
					if (data[i].icon.indexOf("icon-") != -1) {
						ulHtml += '<i class="seraph ' + data[i].icon + '" data-icon="' + data[i].icon + '"></i>';
					} else {
						ulHtml += '<i class="layui-icon" data-icon="' + data[i].icon + '">' + data[i].icon + '</i>';
					}
				}
				ulHtml += '<cite>' + data[i].title + '</cite>';
				ulHtml += '<span class="layui-nav-more"></span>';
				ulHtml += '</a>';
				ulHtml += '<dl class="layui-nav-child">';
				for (var j = 0; j < data[i].children.length; j++) {
					if (data[i].children[j].target == "_blank") {
						ulHtml += '<dd><a href="' + data[i].children[j].href + '" target="' + data[i].children[j].target + '">';
					} else {
						ulHtml += '<dd><a href="' + data[i].children[j].href + '">';
					}
					if (data[i].children[j].icon != undefined && data[i].children[j].icon != '') {
						if (data[i].children[j].icon.indexOf("icon-") != -1) {
							ulHtml += '<i class="seraph ' + data[i].children[j].icon + '" data-icon="' + data[i].children[j].icon +
								'"></i>';
						} else {
							ulHtml += '<i class="layui-icon" data-icon="' + data[i].children[j].icon + '">' + data[i].children[j].icon +
								'</i>';
						}
					}
					ulHtml += '<cite>' + data[i].children[j].title + '</cite></a></dd>';
				}
				ulHtml += "</dl>";
			} else {
				if (data[i].target == "_blank") {
					ulHtml += '<a href="' + data[i].href + '" target="' + data[i].target + '">';
				} else {
					ulHtml += '<a href="' + data[i].href + '">';
				}
				if (data[i].icon != undefined && data[i].icon != '') {
					if (data[i].icon.indexOf("icon-") != -1) {
						ulHtml += '<i class="seraph ' + data[i].icon + '" data-icon="' + data[i].icon + '"></i>';
					} else {
						ulHtml += '<i class="layui-icon" data-icon="' + data[i].icon + '">' + data[i].icon + '</i>';
					}
				}
				ulHtml += '<cite>' + data[i].title + '</cite></a>';
			}
			ulHtml += '</li>';
		}
		return ulHtml;
	}
	//获取二级菜单数据
	Tab.prototype.render = function() {
		//显示左侧菜单
		var _this = this;
		$(".navBar ul").html(
			'<li class="layui-nav-item layui-this"><a href="/index"><i class="layui-icon" data-icon=""></i><cite>首页</cite></a></li>'
			
		).append(_this.navBar(dataStr));
		element.init(); //初始化页面元素
	
	}

	

	//参数设置
	Tab.prototype.set = function(option) {
		var _this = this;
		$.extend(true, _this.tabConfig, option);
		return _this;
	};

	var bodyTab = new Tab();
	exports("bodyTab", function(option) {
		return bodyTab.set(option);
	});
})
