import re
import jieba
import jieba.analyse

def clean(text):
    """
    清洗文本，包括：
    1. 去除@，回复，转发等标志词语
    2. 去除表情符号
    3. 去除超话的#但保留内容
    4. 去除网址
    5. 合并正文的空格

    Args:
        text (str): 微博博文

    Returns:
        str: 清洗后的微博博文
    """
    text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
    text = re.sub(r"\[\S+\]", "", text)      # 去除表情符号
    text = re.sub(r"#\S+#", "", text)      # 保留话题内容
    URL_REGEX = re.compile(
        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
        re.IGNORECASE)
    text = re.sub(URL_REGEX, "", text)       # 去除网址
    text = text.replace("转发微博", "")       # 去除无意义的词语
    text = re.sub(r"\s+", " ", text) # 合并正文中过多的空格
    return text.strip()

def generate_wordcloud_meta(weibo_list):
    """
    根据微博列表生成词云
    1. 首先将所有文本使用jieba分词分成单词
    2. 然后统计每个词出现的频率

    Args:
        weibo_list (list): 某条热搜或方案对应的微博文本列表

    Returns:
        dict: 词云词典
    """
    jieba.analyse.set_stop_words("/home/li/data/repo/Weibo-Public-Opinion-System/peos/crontab_app/word_cloud/cut_word.txt")
    words = []
    wordcloud_meta = {}
    for weibo in weibo_list:
        words.extend(jieba.analyse.extract_tags(clean(weibo), topK=20))
    for word in words:
        if word not in wordcloud_meta.keys():
            wordcloud_meta[word] = 1
        else:
            wordcloud_meta[word] += 1
    return wordcloud_meta