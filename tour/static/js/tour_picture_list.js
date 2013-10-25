$(document).ready(function(){
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

    $("div:contains('With selected')").last().remove();
    $("a[href='/admin/tourpicturefile/upload/']").attr('href', "/admin/tourpicturefile/upload?tour_id="+gup('tour_id'));
})