$(document).ready(function(){
	function add_select() {
        g_detail = $("#detail").val();
		// 添加文件上传
		var picture_select = $.parseHTML("<input class='btn btn-success' type='file' name='picture' id='picture' multiple>");
		$("#picture").replaceWith(picture_select);
	};

	add_select();

    // 定义获取当前url属性的函数
    function gup( name ) {
        name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
        var regexS = "[\\?&]"+name+"=([^&#]*)";
        var regex = new RegExp( regexS );
        var results = regex.exec( window.location.href );
        if( results == null )
            return "";
        else
            return results[1];
    }

    // 如果不是新建的话，添加一个图片管理的东西，到哪里去
    if (g_detail != "") {
        var manager_link = $.parseHTML("<p><a class='btn btn-danger' href='/admin/tourpicturefile?tour_id="+gup('id')+"'>图片管理</a></p>");
        $("#picture").after(manager_link);
        $("#picture").remove();  // 去掉图片上传
    }

	// 表单屏蔽回车提交
    $("input").keypress(function(e) {
        var keyCode = e.keyCode ? e.keyCode : e.which ? e.which : e.charCode;
        if (keyCode == 13) {
            return false;
        } else {
            return true;
        }
    });
});