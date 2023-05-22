from transformers import BertModel
from torch import nn

class BertBasedSentimentModel(nn.Module):
    def __init__(self, hidden_dim, dropout_prob, label_nums):
        super().__init__()
        '''
        Descriptions: 模型1,利用bert <CLS> -> fc  

        Args:
            hidden_dim: bert的隐藏层维度，base版本对应768
            dropout_prob: drop out 概率
            config: bert :BertConfig类
            args: 训练参数，主要用到:
                args.model_name: "bert"or"roberta",如果chinese-roberta-wwm-ext模型，一律使用bert
                self.args.pretrained_model_name: 预训练模型的名字/地址
                args.num_labels: 预测的类别数
        '''

        self.bert =BertModel.from_pretrained("/home/li/data/repo/Weibo-Public-Opinion-System/peos/crontab_app/sentiment/bert/models/")
        self.label_nums = label_nums

        self.dropout = nn.Dropout(dropout_prob)
        self.fc = nn.Linear(hidden_dim, self.label_nums)

    def forward(self, input_ids=None, attention_mask=None):
        '''
        Args:
            input_ids: 输入的向量，维度[batch size, max_len]
            attention_mask: mask矩阵，维度同input_ids,0表示padded index,1表示其他
        Returns:
            logits: 预测向量,维度[batch size, num_labels]
        '''
        x = self.bert(input_ids, attention_mask=attention_mask)
        # x[0]: (batch_size, src_len, hidden_size) : (8,67,768)

        #<CLS>位置对应的输出
        first_hidden_state = x[0][:,0,:]  # (batch_size, hidden_size) : (8, 768)

        x = self.dropout(first_hidden_state)

        logits = self.fc(x)

        return logits