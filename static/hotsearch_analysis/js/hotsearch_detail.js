sentiment_translate = {
    "happy": "高兴",
    "surprise": "惊喜",
    "neutral": "中性",
    "sad": "伤心",
    "fear": "害怕",
    "angry": "生气"
}
color_translate = {
    "happy": "#00a000",
    "surprise": "#FFA500",
    "neutral": "#808080",
    "sad": "#00BFFF",
    "fear": "#000000",
    "angry": "#FF0000"
}

$(document).ready(function () {
    prepare_emotion_rate_chart();
    prepare_word_cloud_chart();
    prepare_emotion_trend_chart();
})
function prepare_emotion_rate_chart() {
    var emotionRateChart = echarts.init(document.getElementById('emotionRateChart'), null, {});
    var happySentimentCount = document.getElementById('happySentimentCount').innerText;
    var surpriseSentimentCount = document.getElementById('surpriseSentimentCount').innerText;
    var sadSentimentCount = document.getElementById('sadSentimentCount').innerText;
    var angrySentimentCount = document.getElementById('angrySentimentCount').innerText;
    var fearSentimentCount = document.getElementById('fearSentimentCount').innerText;
    var neutralSentimentCount = document.getElementById('neutralSentimentCount').innerText;
    emotionRateChart.setOption({
        series: [{
            type: 'pie',
            data: [{
                value: happySentimentCount,
                name: '高兴',
                itemStyle: {color: color_translate['happy']}
            },
            {
                value: surpriseSentimentCount,
                name: '惊喜',
                itemStyle: {color: color_translate['surprise']}
            },
            {
                value: sadSentimentCount,
                name: '悲伤',
                itemStyle: {color: color_translate['sad']}
            },
            {
                value: angrySentimentCount,
                name: '生气',
                itemStyle: {color: color_translate['angry']}
            },
            {
                value: fearSentimentCount,
                name: '害怕',
                itemStyle: {color: color_translate['fear']}
            },
            {
                value: neutralSentimentCount,
                name: '中立',
                itemStyle: {color: color_translate['neutral']}
            }
            ],
            //标签
            label: {
                normal: {
                    show: true,
                    formatter: '{b}:{d}%'
                }
            },
        }]
    })
}

function prepare_word_cloud_chart() {
    var wordCloudChart = echarts.init(document.getElementById('wordCloudChart'));
    //温馨提示：image 选取有严格要求不可过大；，否则firefox不兼容  iconfont上面的图标可以
    var data = []
    wordCloudMeta = eval("(" + document.getElementById("wordCloudMeta").innerText + ")");
    for (const key in wordCloudMeta) {
        data.push({ name: key, value: wordCloudMeta[key] })
    }
    // wordCloudMeta = JSON.parse(document.getElementById("wordCloudMeta").innerText)
    wordCloudChart.setOption({
        backgroundColor: '#fff',
        tooltip: {
            show: true
        },
        series: [{
            type: 'wordCloud',
            gridSize: 1,
            sizeRange: [12, 55],
            rotationRange: [-45, 0, 45, 90],
            // maskImage: maskImage,
            textStyle: {
                normal: {
                    color: function () {
                        return 'rgb(' +
                            Math.round(Math.random() * 255) +
                            ', ' + Math.round(Math.random() * 255) +
                            ', ' + Math.round(Math.random() * 255) + ')'
                    }
                }
            },

            data: data
        }]
    })
}

function prepare_emotion_trend_chart() {
    var sentimentTrendChart = echarts.init(document.getElementById('sentimentTrendChart'));
    sentimentEachDateInverse = {
        "angry": [],
        "sad": [],
        "fear": [],
        "neutral": [],
        "happy": [],
        "surprise": []
    };
    var time_index = Object.keys(sentimentEachDate).sort()
    for (date of time_index) {
        for (sentiment in sentimentEachDate[date]) {
            sentimentEachDateInverse[sentiment].push(sentimentEachDate[date][sentiment])
        }
    }
    sentimentEachDateInverseAccumulate = {}
    for (sentiment in sentimentEachDateInverse) {
        baseArr = sentimentEachDateInverse[sentiment]
        var currNum = 0;
        sentimentEachDateInverseAccumulate[sentiment] = []
        sentimentEachDateInverse[sentiment].forEach((item, index) => {
            if(index == 0){
                sentimentEachDateInverseAccumulate[sentiment].push(baseArr[index]);
            }else{
                if(currNum){
                  currNum = baseArr[index] + currNum;
                }else{
                  currNum = baseArr[index] + baseArr[index-1];
                }
                sentimentEachDateInverseAccumulate[sentiment].push(currNum);
            }
          })
    }
    console.log(sentimentEachDateInverseAccumulate)
    series = []
    for (sentiment in sentimentEachDateInverseAccumulate) {
        series.push({
            name: sentiment_translate[sentiment],
            data: sentimentEachDateInverseAccumulate[sentiment],
            type: 'line',
            color: color_translate[sentiment]
        })
    }
    option = {
        xAxis: {
            type: 'category',
            data: time_index
        },
        yAxis: {
            type: 'value'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            orient: 'horizontal',
            x: 'center',
            y: 'top',
            data: sentiment_translate[Object.keys(sentimentEachDateInverse)]
        },
        backgroundColor: '#fff',
        series: series
    };

    option && sentimentTrendChart.setOption(option);
}