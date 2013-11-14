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
    } else {
        $("#order_max").val(0);
        $("#ordered").val(0);
        $("#rank").val(0);
        $("#stopped").val(0);
    }

    // 获取当前tour的类型
    function get_tour_type() {
       var tour_type = "";
       var id = gup("id");

       if (id) {
           $.ajax({
               type: "GET",
               url: "/restful/admin/tour_type_by_id/" + id,
               dataType: "json",
               async: false,
               cache: false,
               success: function(json) {
                   $.each(json, function(i, value) {
                       tour_type = value;
                   });
               },
               error: function() {
                   alert("获取旅游类型失败");
               }
           });
       };

       return tour_type;
    }
    // 获取全部的类型，同时添加数据
    $.ajax({
        type: "GET",
        url: "/restful/admin/tour_type",
        dataType: "json",
        async: false,
        cache: false,
        success: function(json) {
            var tour_type_select = $.parseHTML("<select name='tour_type_id' id='tour_type_id'></select>");
            $("#tour_type_id").replaceWith(tour_type_select);
            $.each(json, function(i, value) {
                $("#tour_type_id").append($('<option>').text(value[1]).attr('value', value[0]));
                $("#tour_type_id").val(get_tour_type());
                $("#tour_type_id").select2({
                    width: '220px'
                });
            });
        },
    });

    function change_textarea() {
        $("#intro").css('width', '552px').css('height', '60px');
        $("#detail").css('width', '552px').css('height', '400px');
    };
    change_textarea();

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