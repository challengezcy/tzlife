#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# 20200402 修正
# 原因：2020年1到3月份由于新冠疫情导致“垃圾股”的单边下跌，无力反弹，特加入一些基本面的参考因素

__author__ = "challengezcy@163.com"

#python stock_choice.py

#pip install tushare
import tushare as ts
import pandas as pd
import platform
import os

DAYNUM = 22 #过去22天的交易数据
EXPECT = 12 #其中有13次涨跌幅超过5%
NOT_GOOD = 16 #涨跌幅超过5%的有16次，认为这个股票不适合
NO_DIFF = 3 #涨的次数和跌的次数差的绝对值

FLUC_INFO = []

'''ts.get_stock_basics()
#获取2015年第一季度的业绩报表数据
ts.get_report_data(2015,1)
#获取2015年第一季度的盈利能力数据
ts.get_profit_data(2015,1)
#获取2015年第一季度的营运能力数据
ts.get_operation_data(2015,1)
#获取2015年第一季度的成长能力数据
ts.get_growth_data(2015,1)
#获取2015年第一季度的偿债能力数据
ts.get_debtpaying_data(2015,1)
#获取2015年第一季度的现金流量数据
ts.get_cashflow_data(2015,1)
'''

'''ts.get_report_data(年份，季度）, 可以获取每一年的季度的业绩。
   如果想要获取上市公司的年报，只要把季度参数改为4即可'''
def load_report_datas():
	try:
		report = ts.get_report_data(2018, 4)
	except Exception as e:
		print(e)
		report = pd.read_csv("report.csv")

	if (os.path.exists("report.csv")):
		os.remove("report.csv")

	report.fillna(0)
	report.to_csv("report.csv")
	report = pd.read_csv("report.csv")

	return report

def load_all_stock_basics():
	basic = pd.read_csv("basic.csv")
	basic.set_index(['code'], inplace = True)

	return basic

def load_today_all_stocks():
	try:
		df = ts.get_stock_basics()
	except Exception as e:
		print(e)
		df = pd.read_csv("basic.csv")

	if (os.path.exists("basic.csv")):
		os.remove("basic.csv")

	df.to_csv("basic.csv")

	allcode = []
	df = pd.read_csv("basic.csv")
	df.set_index(['code'], inplace = True)
	for i in df.index:
		i = "%06d" % i
		#i = i.zfill(6) 文本型补零
		allcode.append(i)
		#print(i)
	return allcode

def calculate_stock_fluctuation_HZ(stock):
	data = ts.get_k_data(stock, ktype='D', autype='qfq')
	try:
		data = data.sort_values(by='date', ascending=False)
		data = data.set_index('date')
	except KeyError:
		return 0

	if data.shape[0] < DAYNUM + 5:
		return 0

	stock_item = {}
	stock_item['stock'] = stock.zfill(6)
	for j in (1,): #(1,2,3,5)
		fluc_up = 0
		fluc_dw = 0
		fluc = 0
		for i in range(DAYNUM, -1, -1):
			if data.close[i+j] < data.high[i] and round((data.high[i] - data.close[i+j])/(data.close[i+j]),2) > 0.05:
				fluc_up = fluc_up + 1
			if data.close[i+j] > data.low[i] and round((data.close[i+j] - data.low[i])/(data.close[i+j]),2) > 0.05:
				fluc_dw = fluc_dw + 1
		stock_item['aT'] = fluc_up + fluc_dw
		stock_item['adiff'] = abs(fluc_up - fluc_dw)
		stock_item['aup'] = fluc_up
		stock_item['adw'] = fluc_dw
		stock_item['price'] = data.close[i]
		if (stock_item['aT'] < EXPECT or stock_item['aT'] > NOT_GOOD or stock_item['adiff'] > NO_DIFF):
			return 0

	return stock_item

def get_specific_stock_basic(scode, item, basics):
	scode = int(scode)
	name = basics.loc[scode, 'name']
	industry = basics.loc[scode, 'industry']
	area = basics.loc[scode, 'area']
	pe = basics.loc[scode, 'pe']
	pb = basics.loc[scode, 'pb']
	liquidasset = basics.loc[scode, 'liquidAssets']
	fixedasset = basics.loc[scode, 'fixedAssets']
	totalasset = basics.loc[scode, 'totalAssets']
	outstanding = basics.loc[scode, 'outstanding']
	totals = basics.loc[scode, 'totals']
	esp = basics.loc[scode, 'esp']
	bvps = basics.loc[scode, 'bvps']
	reservedpershare = basics.loc[scode, 'reservedPerShare']
	perundp = basics.loc[scode, 'perundp']

	item['pe'] = pe
	item['pb'] = pb
	item['zIdustry'] = str(industry)

def get_specific_stock_extend(scode, item, report):
	tre = report[report['code'] == int(scode)]
	if tre.empty:
		item['roe'] = -99
	else:
		tmp = tre.to_dict(orient='list')
		item['roe'] = tmp['roe'][0]

if __name__ == '__main__':
	if platform.system == 'Windows':
		cmd = 'chcp 936'
		os.system(cmd)

	if (os.path.exists("getItFun.csv")):
		os.remove("getItFun.csv")

	all_code = load_today_all_stocks()
	stock_basics = load_all_stock_basics()
	report_data = load_report_datas()

	i = 0
	for stock in all_code:
		if (i>100):
			break;
		item = calculate_stock_fluctuation_HZ(stock)
		if item != 0:
			get_specific_stock_basic(stock, item, stock_basics)
			get_specific_stock_extend(stock, item, report_data)
			FLUC_INFO.append(item)
		i = i + 1
		print('%d' % i)

	df = pd.DataFrame(FLUC_INFO)
	df.set_index(['stock'], inplace=True)
	df.sort_values(by=['roe'], axis=0, ascending=False, inplace=True)
	print(df)
	df.to_csv("getItFun.csv")
	print("Let's have fun!")

	
	
	

