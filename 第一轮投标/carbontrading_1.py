# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 15:44:28 2017

@author: houqingchun
"""

# %% import package
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

# %% import data
SET = 300
SET_PRICE = 200
FS = 15

pd_1 = pd.read_excel('bid_1.xls', header=0, skiprows=0, names=['序号',	'提交答卷时间',	'所用时间',	
                                                    '来自IP', '来源',	 '来源详情', '姓名',	'学号',	 
                                                    '班级',	'总需求量', '投标量', '投标价格'])
pd_1 = pd_1.sort_values(['投标价格'], ascending=False)
pd_1['累积量'] = np.cumsum(pd_1['投标量'])
pd_1['中标量'] = np.zeros(len(pd_1))
bid_len = len(pd_1[pd_1.累积量 <= SET]['累积量'].values)
pd_1['中标量'].values[0:bid_len] = pd_1[pd_1.累积量 <= SET]['投标量'].values
pd_1['中标量'].values[bid_len] = SET - pd_1['累积量'].values[bid_len-1]


# calculate the bid and penalty price
if pd_1['中标量'].values[bid_len] > 0:
    bid_price = pd_1['投标价格'].values[bid_len]
else:
    bid_price = pd_1['投标价格'].values[bid_len-1]
    
penalty_price = 2 * bid_price
if penalty_price >200:
    penalty_price = 200

# average the bid number when the bid price is same
pd_1.loc[pd_1['投标价格'] == bid_price, ['中标量']] = np.ones(len(pd_1[pd_1['投标价格'] == bid_price]['中标量'])) * np.mean(pd_1[pd_1['投标价格'] == bid_price]['中标量'])

# calculate benefits
pd_1['收益'] = (SET_PRICE - bid_price) * pd_1['中标量'] + (SET_PRICE - penalty_price) * (pd_1['总需求量'] - pd_1['中标量'])

pd_1['班级平均收益'] = np.zeros(len(pd_1))
for cla in ['电51', '电52', '电53', '电54']:
    pd_1.loc[pd_1['班级'] == cla,['班级平均收益']] = np.mean(pd_1[pd_1['班级'] == cla]['收益']) 

# save results to the bid_output.xlsx
pd_2 = pd_1.loc[:, ['姓名',	'学号',	 '班级',	'总需求量', '投标量', '投标价格', '中标量', '收益', '累积量', '班级平均收益']]
writer = pd.ExcelWriter('bid_output_1.xlsx')
pd_2.to_excel(writer,'Sheet1')
writer.save()

prebid_price = np.zeros(2*len(pd_1))
prebid_num = np.zeros(2*len(pd_1))
prebid_price[0::2] = pd_1['投标价格'].values
prebid_price[1::2] = pd_1['投标价格'].values
prebid_num[0::2] = np.append(np.array([0]), pd_1['累积量'].values[0:-1])
prebid_num[1::2] = pd_1['累积量'].values[0:]

plt.figure()
ax = plt.plot(prebid_num, prebid_price)
plt.plot(np.ones(len(prebid_price))*SET, prebid_price )
plt.title(u'第一轮出清曲线', fontsize=FS)
plt.xlabel(u'累积投标量/碳配额', fontsize=FS)
plt.ylabel(u'投标价格/元', fontsize=FS)
plt.grid(True)
plt.text(120, 120, u'出清价格为'+str(bid_price)+u'元', fontsize=FS)
plt.xticks(fontsize=FS)
plt.yticks(fontsize=FS)