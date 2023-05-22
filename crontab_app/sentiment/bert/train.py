from transformers import get_linear_schedule_with_warmup
import torch
from tqdm import tqdm
from torch.utils.data import DataLoader, random_split
import torch.nn
from model import BertBasedSentimentModel

from dataset import SMPDataset


def train(model, train_data_loader, val_data_loader, loss_fn, n_epoch, lr, warmup_steps):
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    # optimizer = AdamW(model.parameters(), lr=args.lr, eps= args.eps)

    scheduler = get_linear_schedule_with_warmup(optimizer,
                                                num_warmup_steps=warmup_steps,
                                                num_training_steps = len(train_data_loader) * n_epoch)
    model = model.to("cuda")
    for epoch in range(n_epoch):
        #训练epoch轮
        model.train()
        epoch_loss = 0
        min_valid_loss = 1000
        # train
        for data in tqdm(train_data_loader):
            optimizer.zero_grad()
            inputs, masks, labels = data
            outputs = model(inputs, attention_mask = masks)

            loss = loss_fn(input=outputs, target=labels)

            loss.backward()
            optimizer.step()
            scheduler.step()

            # if i % 10 == 0:
            #     print("Batch: {}, loss :{} ".format(i,loss.item()))

            epoch_loss  += loss.item()
        train_loss = epoch_loss / len(train_data_loader)
        
        # validate
        model.eval()
        epoch_loss = 0
        hit = 0
        total = 0
        with torch.no_grad():
            for i, data in enumerate(val_data_loader):

                inputs, masks, labels = data
                outputs = model(inputs, attention_mask = masks)

                preds = torch.argmax(outputs, dim=1)  # 每一行的最大值下标

                loss = loss_fn(input=outputs, target=labels)

                hit += sum(labels == preds).item()
                total += len(labels)

                epoch_loss  += loss.item()

            print("valid acc: {}".format(hit/total))
        valid_loss = epoch_loss / len(val_data_loader)
        #比较之前的最好验证集损失，如果当前较好，覆盖之前模型
        if valid_loss < min_valid_loss:
            min_valid_loss = valid_loss
            torch.save(model, 'models/best_valid_model.pt')
        #每轮骨骺保存模型，防止断电
        torch.save(model, 'models/last_model.pt')

        print("Epoch:{}, avg_train_loss: {}, avg_valid_loss: {}".format(epoch,train_loss,valid_loss))

if __name__=="__main__":
    dataset = SMPDataset("../../../data/SMP2022/train/virus_train.xlsx")
    train_data, val_data = random_split(dataset, [int(0.8*len(dataset)), len(dataset)-int(0.8*len(dataset))])
    train_data_loader = DataLoader(train_data, batch_size=32)
    val_data_loader = DataLoader(val_data, batch_size=32)
    model = BertBasedSentimentModel(hidden_dim=768, dropout_prob=0.2, label_nums=6)
    loss_fn = torch.nn.CrossEntropyLoss()
    train(model, train_data_loader, val_data_loader, loss_fn, n_epoch=6, lr=0.001, warmup_steps=1000)