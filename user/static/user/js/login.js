function login()
{
    loginUsername = $("input[name=loginUsername]").val()
    // loginPassword_md5 = md5($("input[name=loginPassword]").val())
    loginPassword = $("input[name=loginPassword]").val()
    $.ajax({
        type: "POST",
        url: "/user/login/",
        dataType: 'json',
        data: {
            loginUsername: loginUsername,
            loginPassword: loginPassword
        },
        success: function (res) {
            let code = res.code;
            let msg = res.msg;
            if (code == 1) {
                //2021.7.26，跳转修改为数据监测页面
                let uid = res.uid
                console.log(uid)
                window.location.href = "/home/"+ uid+"/"
            } else {
                commonUtil.message(msg, "danger");
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            if (xhr.status == 403) {
                window.location.href = ctxPath + "login";
            }
        }
    });
    
}

