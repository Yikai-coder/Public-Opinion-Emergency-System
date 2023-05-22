from transformers import BertTokenizer
import torch
from torch.utils.data import Dataset
import re
import pandas as pd

class sentimentDataset(Dataset):
    def __init__(self, reviews, labels=None):
        self.padding_max = 128
        self.tokenizer = BertTokenizer.from_pretrained("/home/li/data/repo/Weibo-Public-Opinion-System/peos/crontab_app/sentiment/bert/models/chinese-roberta-wwm-ext")
        self.padded, self.mask = self.padding(self.tokenizer(reviews))
        self.padded = self.padded.to("cuda")
        self.mask = self.mask.to("cuda")
        self.labels = None
        if labels != None:
            self.labels = torch.tensor(labels).to("cuda")

    def __len__(self):
        return len(self.padded)

    def __getitem__(self, index):
        if self.labels == None:
            return self.padded[index], self.mask[index]
        else:
            return self.padded[index], self.mask[index], self.labels[index]

    def padding(self, reviews):
        '''
        Descriptions:
            将每个样本补全到最大长度，超出的部分忽略，生成mask向量
        Returns:
            padded:补全后的向量矩阵
            attention_mask: mask矩阵
        '''
        max_len = 0
        for i in reviews['input_ids']:
            if len(i) > max_len:
                max_len = len(i)

        if max_len > self.padding_max:
            max_len = self.padding_max

        padded = []

        for i in reviews['input_ids']:
            if(len(i) > max_len):
                padded.append(i[:max_len -1 ] +[i[-1]])
            else:
                padded.append(i + [self.tokenizer.pad_token_id] * (max_len - len(i)))

        # padded = np.array(padded)
        padded = torch.tensor(data=padded)

        # attention_mask = np.where(padded != self.tokenizer.pad_token_id, 1, 0)    #mask 机制
        attention_mask = torch.where(padded != self.tokenizer.pad_token_id, 1, 0)
        return padded, attention_mask

class senti100kDataset(sentimentDataset):
    """_summary_

    Args:
        sentimentDataset (_type_): _description_
    """
    def __init__(self, file_path):
        reviews, labels = pd.read_csv(file_path)["review"], pd.read_csv(file_path)["label"]
        with open('./cut_word.txt','r+',encoding='utf-8') as cutword_file:
            stopwords=cutword_file.read().split('\n')
            clean_reviews = []
            clean_labels = []
            for review, label in zip(reviews, labels):
                clean_review = self.clean(review)
                if clean_review == "":
                    continue
                clean_reviews.append(clean_review)
                clean_labels.append(label)

        super().__init__(clean_reviews, clean_labels)

    def clean(self, text):
        text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
        text = re.sub(r"\[\S+\]", "", text)      # 去除表情符号
        # text = re.sub(r"#\S+#", "", text)      # 保留话题内容
        URL_REGEX = re.compile(
            r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
            re.IGNORECASE)
        text = re.sub(URL_REGEX, "", text)       # 去除网址
        text = text.replace("转发微博", "")       # 去除无意义的词语
        text = re.sub(r"\s+", " ", text) # 合并正文中过多的空格
        return text.strip()

class SMPDataset(sentimentDataset):
    label_to_num = {
        "angry": 0,
        "sad": 1,
        "fear": 2,
        "neutral": 3,
        "happy": 4,
        "surprise": 5
    }
    def __init__(self, file_path):
        reviews, str_labels = pd.read_excel(file_path)["文本"], pd.read_excel(file_path)["情绪标签"]
        labels = [self.label_to_num[str_label] for str_label in str_labels]
        with open('./cut_word.txt','r+',encoding='utf-8') as cutword_file:
            stopwords=cutword_file.read().split('\n')
            clean_reviews = []
            clean_labels = []
            for review, label in zip(reviews, labels):
                clean_review = self.clean(review)
                if clean_review == "":
                    continue
                clean_reviews.append(clean_review)
                clean_labels.append(label)
        super().__init__(clean_reviews, clean_labels)


    def clean(self, text):
        text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
        text = re.sub(r"\[\S+\]", "", text)      # 去除表情符号
        # text = re.sub(r"#\S+#", "", text)      # 保留话题内容
        URL_REGEX = re.compile(
            r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
            re.IGNORECASE)
        text = re.sub(URL_REGEX, "", text)       # 去除网址
        text = text.replace("转发微博", "")       # 去除无意义的词语
        text = re.sub(r"\s+", " ", text) # 合并正文中过多的空格
        return text.strip()

class testDataset(sentimentDataset):
    label_to_num = {
        "angry": 0,
        "sad": 1,
        "fear": 2,
        "neutral": 3,
        "happy": 4,
        "surprise": 5
    }

    def __init__(self, weibo_list):
        clean_text = []
        for text in weibo_list:
            clean_text.append(self.clean(text))
        super().__init__(clean_text)
            

    def clean(self, text):
        text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
        text = re.sub(r"\[\S+\]", "", text)      # 去除表情符号
        # text = re.sub(r"#\S+#", "", text)      # 保留话题内容
        URL_REGEX = re.compile(
            r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
            re.IGNORECASE)
        text = re.sub(URL_REGEX, "", text)       # 去除网址
        text = text.replace("转发微博", "")       # 去除无意义的词语
        text = re.sub(r"\s+", " ", text) # 合并正文中过多的空格
        text = text.replace("\n", "") # 去除换行符
        return text.strip()    