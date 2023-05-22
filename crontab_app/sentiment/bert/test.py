import sys
sys.path.append("/home/li/data/repo/Weibo-Public-Opinion-System/peos/crontab_app/sentiment/bert")
from dataset import testDataset
from torch.utils.data import DataLoader
import torch
import pandas as pd

def test(weibo_list):
    """
    调用情感分析模型对微博进行情感分析

    Args:
        weibo_list (list): 微博文本列表

    Returns:
        list: 每条微博对应的情感(0-5)
    """
    dataset = testDataset(weibo_list)
    test_dataloader = DataLoader(dataset, batch_size=32)
    
    model = torch.load("/home/li/data/repo/Weibo-Public-Opinion-System/peos/crontab_app/sentiment/bert/models/best_valid_model.pt")
    model.eval()
    ans = []
    # for data in tqdm(test_dataloader):
    for _, data in enumerate(test_dataloader):
        inputs, masks = data
        outputs = model(inputs, attention_mask = masks)

        preds = torch.argmax(outputs, dim=1)  # 每一行的最大值下标

        ans.extend(preds.tolist())
    torch.cuda.empty_cache() # 清除显存   
    return ans

if __name__=="__main__":
    text = pd.read_csv("./shenzhen.csv")["微博正文"].values.tolist()
    ans = test(text)
    num_to_label = [
        "angry",
        "sad",
        "fear",
        "neutral",
        "happy",
        "surprise"
    ]
    with open("predict.csv", "w") as f:
        for weibo, label in zip(text, ans):
            f.write("%s, %s\n" % (weibo, num_to_label[label]))
