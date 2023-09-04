# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/9/1 11:17
# @File    : datasetModify.py
# @Software: PyCharm
# 读取某path文件夹下所有文件，并拿到文件名
import os
import tqdm
import shutil
import xml.etree.ElementTree as ET
def formatTheFileName(srcPath):
    '''
    将文件夹下面的所有文件名格式化，不包括文件后缀
    在文件名中，如果遇到。变为_
        如果遇到.rt变为_rt
        如果遇到.XX变为_xx
    Args:
        srcPath ():

    Returns:

    '''
    # 使用tqdm显示进度条
    for root, dirs, files in (os.walk(srcPath)):
        for file in tqdm.tqdm(files):
            # 拿到文件名
            filename = os.path.splitext(file)[0]
            # 拿到文件后缀
            filetype = os.path.splitext(file)[1]
            # 替换文件名中的.为_
            filename = filename.replace('.', '_')
            # 写回文件名
            os.rename(os.path.join(root, file), os.path.join(root, filename + filetype))
def trasform(srcPath, targetTxtPath):
    '''

    Args:
        srcPath (): 要读入的anatation文件夹
        targetTxtPath (): 要写入的txt路径

    Returns:

    '''
    # 最终将结果要写入txt
    testF = open(os.path.join(targetTxtPath,'test_list.txt'), 'w')
    trainF = open(os.path.join(targetTxtPath,'train_list.txt'), 'w')
    validF = open(os.path.join(targetTxtPath,'valid_list.txt'), 'w')
    # 使用tqdm显示进度条
    count= 0
    for root, dirs, files in (os.walk(srcPath)):
        for file in tqdm.tqdm(files):
            # 拿到文件名
            filename = os.path.splitext(file)[0]
            # 拿到文件后缀
            filetype = os.path.splitext(file)[1]
            # 判断文件后缀是否为.xml
            if filetype == '.xml':
                # 对于每10个，取一个作为验证集，取2个作为测试集，剩下的作为训练集
                if count % 10 == 0:
                    validF.write('JPEGImages/' + filename + '.jpg' + ' ' + 'Annotations/' + filename + '.xml' + '\n')
                elif count % 10 == 1 or count % 10 == 2:
                    testF.write('JPEGImages/' + filename + '.jpg' + ' ' + 'Annotations/' + filename + '.xml' + '\n')
                else:
                    trainF.write('JPEGImages/' + filename + '.jpg' + ' ' + 'Annotations/' + filename + '.xml' + '\n')
            count += 1

def moveFile(srcPath, targetPath, format='.xml'):
    '''
    #将某个文件夹下的所有以(format).xml结尾的文件全部转移到另一个文件夹下
    Args:
        srcPath ():
        targetPath ():
        format ():

    Returns:

    '''
    # 使用tqdm显示进度条
    for root, dirs, files in tqdm.tqdm(os.walk(srcPath)):
        for file in tqdm.tqdm(files):
            # 拿到文件后缀
            filetype = os.path.splitext(file)[1]
            # 判断文件后缀是否为.xml
            if filetype == format:
                # 复制该文件粘贴到targetPath下
                # # 源文件路径
                # print(os.path.join(root,file))
                # # 目标文件路径
                # print(os.path.join(targetPath,file))
                shutil.copy(os.path.join(root, file), os.path.join(targetPath, file))

# 程序功能：批量修改VOC数据集中xml标签文件的标签名称
def changelabelname(inputpath):
    listdir = os.listdir(inputpath)
    listdir = tqdm.tqdm(listdir)
    for file in listdir:
        if file.endswith('xml'):
            file = os.path.join(inputpath, file)
            tree = ET.parse(file)
            root = tree.getroot()
            for object1 in root.findall('object'):
                for sku in object1.findall('name'):  # 查找需要修改的名称
                    if (sku.text == 'smoke'):  # ‘preName’为修改前的名称
                        sku.text = 'fork'  # ‘TESTNAME’为修改后的名称
                        tree.write(file, encoding='utf-8')  # 写进原始的xml文件并避免原始xml中文字符乱码
                    else:
                        pass

        else:
            pass

if __name__ == '__main__':

    # 修改标签名称
    inputpath = r'D:\IHCOMMON-test\DataSet\待合并的IH数据集\D0004\Annotations'
    changelabelname(inputpath)

    # # 执行格式化文件名
    # srcPath = r'D:\IHCOMMON-test\DataSet\IH-RTDETR-test-91\Annotations'
    # formatTheFileName(srcPath)
    # srcPath = r'D:\IHCOMMON-test\DataSet\IH-RTDETR-test-91\JPEGImages'
    # formatTheFileName(srcPath)
    # # 执行转换自动生成txt文件
    # srcPath = r'D:\IHCOMMON-test\DataSet\HardHatSamplev8ivoc\test\annotations'
    # targetTxtPath = 'D:\IHCOMMON-test\DataSet\IH-RTDETR-test-91'
    # trasform(srcPath, targetTxtPath)

    # # 执行复制
    # srcpath = 'D:\IHCOMMON-test\DataSet\HardHatSamplev8ivoc\\train'
    # targetPath = 'D:\IHCOMMON-test\DataSet\IH-RTDETR-test-91\Annotations'
    # format = '.xml'
    # moveFile(srcpath,targetPath,format)
    # srcpath = 'D:\IHCOMMON-test\DataSet\HardHatSamplev8ivoc\\valid'
    # targetPath = 'D:\IHCOMMON-test\DataSet\IH-RTDETR-test-91\Annotations'
    # format = '.xml'
    # moveFile(srcpath,targetPath,format)
    #
    # srcpath = 'D:\IHCOMMON-test\DataSet\HardHatSamplev8ivoc\\train'
    # targetPath = 'D:\IHCOMMON-test\DataSet\IH-RTDETR-test-91\JPEGImages'
    # format = '.jpg'
    # moveFile(srcpath,targetPath,format)
    # srcpath = 'D:\IHCOMMON-test\DataSet\HardHatSamplev8ivoc\\valid'
    # targetPath = 'D:\IHCOMMON-test\DataSet\IH-RTDETR-test-91\JPEGImages'
    # format = '.jpg'
    # moveFile(srcpath,targetPath,format)
