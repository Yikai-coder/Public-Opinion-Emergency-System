function register() {
    registerUsername = $("input[name=registerUsername]").val()
    registerEmail = $('input[name=registerEmail').val()
    registerPassword = $("input[name=registerPassword]").val()
    $.ajax({
        type: "POST",
        url: "/user/register/",
        dataType: 'json',
        data: {
            registerUsername: registerUsername,
            registerEmail: registerEmail,
            registerPassword: registerPassword
        },
        success: function (res) {
            let code = res.code;
            let msg = res.msg;
            if (code == 1) {
                /*window.location.href = "/displayboard";*/
                //2021.7.26，跳转修改为数据监测页面
                window.location.href = "/user/login/"
            } else if (code == 4) {
                alert(msg);
            } else {
                commonUtil.message(msg, "danger");
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            if (xhr.status == 403) {
                window.location.href = ctxPath + "register";
            }
        }
    });
}