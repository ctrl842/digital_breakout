from imutils import paths
import torch as tr
import torchvision as trv
import pandas as pd
import numpy as np
import os
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

class sumData(tr.utils.data.Dataset):
    def __init__(self, dirs, transform):
        self.main_dir = dirs
        self.transform = transform
    
    def __len__(self):
        return len(self.main_dir)

    def __getitem__(self, idx):
        img_loc = os.path.join(self.main_dir[idx])
        image = Image.open(img_loc).convert("RGB")
        w, h = image.size
        image = image.crop((0, 30, w, h-100))
        tensor_image = self.transform(image)
        return tensor_image


class Data:
    def __init__(self,
                 path_to_file:str):
        self.main_dir = np.array(sorted(list(paths.list_images(path_to_file))))
        self._set_param()

    class sumData(tr.utils.data.Dataset):
        def __init__(self, dirs, transform):
            self.main_dir = dirs
            self.transform = transform

        def __len__(self):
            return len(self.main_dir)

        def __getitem__(self, idx):
            img_loc = os.path.join(self.main_dir[idx])
            image = Image.open(img_loc).convert("RGB")
            w, h = image.size
            image = image.crop((0, 30, w, h-100))
            tensor_image = self.transform(image)
            return tensor_image

    def _create_data(self):

        data_transforms = trv.transforms.Compose([
                trv.transforms.Resize(256),
                trv.transforms.CenterCrop(256),
                trv.transforms.ToTensor(),
                trv.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        
        data = self.sumData(self.main_dir,data_transforms)
        data_loader = tr.utils.data.DataLoader(data,self.batch_size,shuffle=False)
        return data_loader
        
    def _set_param(self):
        self.batch_size = 16 if len(self.main_dir)>16 else 1
        self.device = tr.device('cuda') if tr.cuda.is_available() else tr.device('cpu')
        model = trv.models.resnet152(weights='IMAGENET1K_V2')
        num_ftrs = model.fc.in_features
        model.fc = tr.nn.Linear(num_ftrs, 3)
        model.load_state_dict(tr.load('ResNet_152_3_classes__.pt',map_location=self.device))
        self.model = model

    def _pred_val(self,dataset):
        self.model.eval()
        label = []
        for _,inputs in enumerate(dataset):
            inputs = inputs.to(self.device)
            with tr.no_grad():
                label.append(self.model(inputs))
        resul = tr.cat(label).cpu().argmax(1)
        temp = np.zeros([resul.shape[0],3]).astype(int)
        for i in range(len(temp)):
            temp[i,resul[i]] = 1
        return temp
        
    def get_result(self):
        temp = self._pred_val(self._create_data())
        data = pd.DataFrame(self.main_dir,columns=['filename'])
        data[['broken','empty','animals']] = temp
        return data



    
    
