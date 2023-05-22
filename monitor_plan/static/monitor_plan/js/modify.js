function submitModification() {
    var arr = window.location.href.split('/')
    console.log(arr, arr.length)
    plan_id = arr[arr.length-2]
    plan_name = $("input[id=plan_name]").val()
    plan_description = $("textarea[id=plan_description]").val()
    plan_keywords = $("textarea[id=plan_keywords]").val().replace(/\s+/g, "").split(",")
    plan_excludewords = $("textarea[id=plan_excludewords]").val().replace(/\s+/g, "").split(",")
    console.log(plan_keywords)
    $.ajax({
        type: "post",
        url: "/monitor_plan/modify/"+plan_id+"/",
        data: {
            plan_id: plan_id,
            plan_name: plan_name,
            plan_description: plan_description,
            plan_keywords: plan_keywords,
            plan_excludewords: plan_excludewords
        },
        dataType: "json",
        success: function (response) {
            if (response.code != 1)
            {
                window.location.href("/user/login/");
                commonUtil.message(response.msg, "danger");
            }
            else{
                window.history.go(-1)
                commonUtil.message("修改成功", "success")
            }
        },

    });
}

function cancelModification() {
    window.history.go(-1)
}