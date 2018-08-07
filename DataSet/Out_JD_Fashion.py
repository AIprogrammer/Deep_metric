from __future__ import absolute_import, print_function
"""
In-shop-clothes data-set for Pytorch
"""
import torch
import torch.utils.data as data
from PIL import Image
import os
from torchvision import transforms
from collections import defaultdict
import random

# Solve IOError
from PIL import ImageFile
from torch.backends import cudnn

cudnn.benchmark = True

ImageFile.LOAD_TRUNCATED_IMAGES = True


def default_loader(path, area=None):
    if area is None:
        return Image.open(path).convert('RGB')
    else:
        return Image.open(path).crop(area).convert('RGB')


class JD_Data(data.Dataset):

    def __init__(self, imgs=None, labels=None, areas=None, loader=default_loader, transform=None):

        # Initialization data path and train(gallery or query) txt path

        self.images = imgs
        self.labels = labels
        self.areas = areas

        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])

        if transform is None:
            transform = transforms.Compose([
                # transforms.CovertBGR(),
                transforms.Resize(256),
                transforms.RandomRotation(degrees=30),
                transforms.RandomResizedCrop(scale=(0.16, 1), size=224),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                normalize,
            ])

        # read txt get image path and labels

        classes = list(set(labels))

        # Generate Index Dictionary for every class
        Index = defaultdict(list)
        for i, label in enumerate(labels):
            Index[label].append(i)

        # Initialization Done
        self.classes = classes
        self.transform = transform
        self.Index = Index
        self.loader = loader

    def __getitem__(self, index):

        if self.areas is not None:

            fn, label, area = self.images[index], self.labels[index], self.areas[index]
            img = self.loader(fn, area=area)
        else:
            fn, label = self.images[index], self.labels[index]
            img = self.loader(fn)

        if self.transform is not None:
            img = self.transform(img)
        return img, label

    def __len__(self):
        return len(self.images)


class Out_JD_Fashion:
    def __init__(self, root=None, transform=None, crop=False):
        # Data loading code
        self.crop = crop

        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])

        if transform is None:
            transform = [transforms.Compose([
                # transforms.CovertBGR(),
                transforms.Resize(256),
                # transforms.RandomRotation(degrees=15),
                transforms.RandomResizedCrop(scale=(0.16, 1), size=224),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                normalize,
            ]),
                transforms.Compose([
                    # transforms.CovertBGR(),
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    normalize,
                ]),
                transforms.Compose([
                    # transforms.CovertBGR(),
                    transforms.Resize(224),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    normalize,
                ]),
            ]

        if root is None:
            root = "/home/xunwang/jd-fashion-images"

        random.seed(1)
        label_txt = os.path.join(root, 'labels/fashion_search_field_md5_0515.txt')

        data_dir = '/home/xunwang/jd-fashion-images'

        # read txt get image path and labels
        file = open(label_txt)
        images_anon = file.readlines()
        # random.shuffle(images_anon)
        # print(images_anon[0])
        images = []
        labels = []
        # areas = []

        for i, img_anon in enumerate(images_anon):
            # if i == 0:
                # print(img_anon)
            # img_anon = img_anon.replace('com/', ' ')
            img_anon = img_anon.split(' ')
            img = os.path.join(data_dir, img_anon[0])
            label_ = int(img_anon[1])
            images.append(img)
            labels.append(label_)
            # break

        # print(labels[-100:])

        # print(os.path.exists(images[300]))

        # all as train except last 1000 images
        N_train = len(images_anon) - 1000

        train_imgs = images[:N_train]
        train_labels = labels[:N_train]

        val_imgs = images[N_train:]
        val_labels = labels[N_train:]

        if self.crop:
            pass
            # self.train = JD_Data(imgs=train_imgs, labels=train_labels, areas=train_areas, transform=transform[0])
            # self.gallery = JD_Data(imgs=val_imgs, labels=val_labels, areas=val_areas, transform=transform[2])
        else:
            self.train = JD_Data(imgs=train_imgs, labels=train_labels, transform=transform[0])
            self.gallery = JD_Data(imgs=val_imgs, labels=val_labels, transform=transform[1])

        # self.query = JD_Data(root, label_txt=query_txt, transform=transform[1])


def test_Out_JD_Fashion():
    data = Out_JD_Fashion(crop=False)

    img_loader = torch.utils.data.DataLoader(
        data.gallery, batch_size=4, shuffle=True, num_workers=16)

    for index, batch in enumerate(img_loader):
        # print(img)
        print(batch[0].shape)
        print(index)
        break

    print(len(data.gallery))
    # print(len(data.train))

if __name__ == "__main__":
    test_Out_JD_Fashion()