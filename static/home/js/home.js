$(".table-hover").bootstrapTable({
    pagination: true,   //是否显示分页条
    pageSize: 5,   //一页显示的行数
    paginationLoop: false,   //是否开启分页条无限循环，最后一页时点击下一页是否转到第一页
});

function plan_delete(plan_id) {
    console.log(plan_id);
    $("#delModal").modal('show');
    $('#confirmDeleteBtn').click(function () {
        $("#delModal").modal('hide')
        $.ajax({
            url: '/monitor_plan/delete/',
            type: 'get',
            dataType: 'json',
            data: {
                plan_id: plan_id
            },
            success: function (res) {
                window.location.reload();
                commonUtil.message("删除成功", "success");
            },
            error: function (xhr, ajaxOptions, thrownError) {
                if (xhr.status == 403) {
                    window.location.href = ctxPath + "login";
                } else {
                    $("#popularinformation").css({"position": "relative", "min-height": "300px"})
                    dataerror("#popularinformation")
                }
            }
        });
    })
}