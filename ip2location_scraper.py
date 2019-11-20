#!/usr/bin/python
import os
import sys
import json
import inspect
import csv
import time
from random import randrange
from datetime import datetime
import argparse
import logging
import clearbit
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
# from ipwhois import IPWhois
root_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir) 
# print root_dir
logging.basicConfig(
	format='[%(asctime)s > %(module)s:%(lineno)d %(levelname)s]:%(message)s',
	level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p',
	#filename='apps_uploader_details.log'
)
logger = logging.getLogger(__name__)
def login_ip2location(username,password):
	driver = webdriver.Chrome()
	driver.get("https://www.ip2location.com/login'")
	user=driver.find_element_by_id('emailAddress').send_keys(username)
	pswd=driver.find_element_by_id('password').send_keys(password)
	driver.find_element_by_name('btnLogin').click()
	#time.sleep(2)
	return driver

def get_information(html):
	infolist = []
	temp = []
	soup = BeautifulSoup(html,"lxml")
	items = soup.find_all(style = 'vertical-align:middle;')
	for item in items:
		infolist.append(item.string)
	for item in items[1].descendants:
		temp.append(item)
	infolist[1] = temp[1]
	return infolist
def ip_util(i, o):
	driver = login_ip2location(username,password)
	infile = i
	outfile= o
	c = None
	this_function_name = sys._getframe().f_code.co_name
	frame = inspect.currentframe()
	args, _, _, values = inspect.getargvalues(frame)
	
	logger.info("IN func: {}".format(values.get('this_function_name','')))
	logger.info("infile: {}".format(values.get('i','')))
	logger.info("outfile: {}".format(values.get('o','')))

	if not i:
		raise Exception("infile is Required")
	if not o:
		raise Exception("outfile is Required")
	try:
		lines = list( csv.DictReader(open(infile)))
		t_lines = len(lines)
		details_headers = ['IP Address', 'Location', 'Latitude & Longitude','ISP','Local Time','Domain','Net Speed',
					'IDD & Area Code','ZIP Code','Weather Station','Mobile Country Code (MCC)',
					'Mobile Network Code (MNC)','Carrier Name','Elevation',
					'Usage Type','Anonymous Proxy','Proxy Type','Shortcut','Twitterbot','Slackbot']
		for i,line in enumerate(lines):
			data = {}
			try:
				sr=line.get('sr')
				ip_addr = line.get('Anonymous_IP')
				logging.info("\n{}\n".format("^"*80))
				logging.info(
					"Input CSV =====>>\n"
					"{}\n"
					"".format(
					line
					)
				)
				if ip_addr:
					driver.get('https://www.ip2location.com/demo/' + ip_addr)
					url_source=driver.page_source
					details = get_information(url_source)
					data.update({h:details[index] for index, h in enumerate(details_headers)})

				data.update({'sr':sr,'Anonymous_IP':ip_addr})


				print ('---------------------')
				print ('after scraping')
				print(data)
			except Exception as e:
				logger.error("Error: [{0}] at line [{1}]".format(
					str(e), sys.exc_info()[2].tb_lineno)
				)
			filemode = 'wb' if i==0 else 'a' 
			header=['sr','Anonymous_IP']
			header.extend(details_headers)
			dump_dict_array_to_csv(inp_dict_array=[data],outcsv=outfile,filemode=filemode,ordered_headers=header)

			# with open(o,filemode) as f:
			# 	writer = csv.writer(f)
			# 	writer.writerow(header)
			# 	writer.writerows(data)		
	except Exception as e:
		logger.error("Error: [{0}] IN export at line [{1}]".format(
			str(e), sys.exc_info()[2].tb_lineno)
		)


def dump_dict_array_to_csv(inp_dict_array, outcsv,
                               csv_delimeter=',', filemode='wb',
                               ordered_headers=[],encoding='utf-8'):
        try:
            keys = ordered_headers if ordered_headers else inp_dict_array[0].keys()
            with open(outcsv, filemode) as output_file:
                if filemode == 'a':
                    header = False
                else:
                    header = True
                df = pd.DataFrame(inp_dict_array, columns=keys)
                df.to_csv(output_file, sep=str(csv_delimeter), index=False, header=header,encoding='utf-8')
                return df
        except Exception as e:
            logging.error("Error is [{0}] at line [{1}]".format(
                str(e), sys.exc_info()[2].tb_lineno)
            ) 


# def write_to_csv(infolist):
# 	with open('1_150.csv','w') as f:
#     writer = csv.writer(f)
#     writer.writerows(['IP Address', 'Location', 'Latitude & Longitude','ISP','Local Time','Domain','Net Speed','IDD & Area Code'
#     				'ZIP Code','Weather Station','Mobile Country Code (MCC)','Mobile Network Code (MNC)','Carrier Name',
#     				'Elevation','Usage Type','Anonymous Proxy','Shortcut','Twitterbot','Slackbot'])
#     writer.writerows(infolist)
# 	# for item in infolist:
# 		#print item.encode('utf-8')
	# return infolist

	#infolist
	#--------
	#IP Address
	#Location
	#Latitude & Longitude
	#ISP
	#Local Time
	#Domain
	#Net Speed
	#IDD & Area Code
	#ZIP Code
	#Weather Station
	#Mobile Country Code (MCC)
	#Mobile Network Code (MNC)
	#Carrier Name
	#Elevation
	#Usage Type
	#Anonymous Proxy
	#Shortcut
	#Twitterbot
	#Slackbot

if __name__ == '__main__':
	# username, password  = 'modric.funnel@gmail.com',  'sayb21'
	# driver = login_ip2location(username, password)
	# driver.get('https://www.ip2location.com/demo/')
	# # print driver.page_source.encode('utf-8')
	# print get_information(driver.page_source)

	parser = argparse.ArgumentParser(
		description="ip2location and Out CSV"
	)

	# driver=webdriver.Chrome()

	parser.add_argument("--i", metavar="infile",
					  help="input file path", default='input.csv')
	parser.add_argument("--o", metavar="outfile",
					  help="output file path", default='output.csv')
   
	params = parser.parse_args().__dict__.items()

	params = dict(params)

	parser.print_help()

	try:
		username, password  = 'username',  'pass'
		# driver = login_ip2location(username, password)
		# login_ip2location(username, password)
		ip_util(**params)

	except Exception as e:
		logger.error("In export: [{}]".format(e))

	print ("*" * 100)



