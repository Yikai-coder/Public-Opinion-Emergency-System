custom_settings_for_keyword_search_spider = {
    "ITEM_PIPELINES":{
        'weibo.pipelines.HotSearchPipeline':100
    },
    "CLOSESPIDER_TIMEOUT": 1800
}

custom_settings_for_hotsearch_spider = {
    "ITEM_PIPELINES":{
        'weibo.pipelines.HotSearchPipeline':100
    }
}

custom_settings_for_url_spider = {
    "ITEM_PIPELINES":{
        'weibo.pipelines.WeiboPipeline':100
    },
    "CLOSESPIDER_ITEMCOUNT": 180
}

custom_settings_for_comment_spider = {
    "ITEM_PIPELINES":{
        'weibo.pipelines.CommentPipeline':100
    }
}

custom_settings_for_user_spider = {
    "ITEM_PIPELINES":{
        'weibo.pipelines.UserPipeline':100
    }
}