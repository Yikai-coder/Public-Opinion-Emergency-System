function trace_hotsearch(hotsearch_id, uid)
{
    $.ajax({
        url: '/hotsearch_analysis/trace/',
        type: 'post',
        dataType: 'json',
        data: {
            hotsearch_id: hotsearch_id,
            uid: uid
        },
        success: function (res) {
            commonUtil.message("已加入监控", "success");
            window.location.reload();
        },
        error: function (xhr, ajaxOptions, thrownError) {
            if (xhr.status == 403) {
                window.location.href = ctxPath + "login";
            } else {
                // $("#popularinformation").css({"position": "relative", "min-height": "300px"})
                // dataerror("#popularinformation")
                console.log("Error");
            }
        }
    });

}