#!/usr/bin/python3.5

import requests
import lxml.html as lh
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
from time import sleep
import json as j
import argparse

def main(position,outfile):
	url = 'https://www.footballdb.com/fantasy-football/index.html?pos={0}'.format(position)
	url = url + '&yr={0}&wk=all&rules=2'
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

	col_map = {
		0 : 'Player',
		1 : 'Bye',
		2 : 'Fantasy_Points',
		3 : 'Pass_Att',
		4 : 'Pass_Cmp',
		5 : 'Pass_Yds',
		6 : 'Pass_TDs',
		7 : 'Pass_INTs',
		8 : 'Pass_2Pt_Conv',
		9 : 'Rush_Att',
		10 : 'Rush_Yds',
		11 : 'Rush_TDs',
		12 : 'Rush_2Pt_Conv',
		13 : 'Rec',
		14 : 'Rec_Yds',
		15 : 'Rec_TDs',
		16 : 'Rec_2Pt_Conv',
		17 : 'Fumble_Lost',
		18 : 'Fumble_TD_Rec'
	}
	
	players = {}
	blacklist = []

	for yr in list(range(2010,2019,1)):
		print(str(yr))
		url_yr = url.format(yr)
		page = requests.get(url_yr,headers=headers)
		doc = lh.fromstring(page.content)
		tr_elements = doc.xpath('//tr')
		for t in tr_elements:
			if len(t) != 19:
				continue
			elif t[0].text_content().lower() == 'player':
				continue
			for ix, t1 in enumerate(t):
				if ix == 0:
					player = '.'.join(t1.text_content().split('.')[:-1])[:-1]
					if player not in players:
						players[player] = {}
						players[player]['data'] = {}
						players[player]['attrib'] = {}
					if 'dob' not in players[player]['attrib'] and player not in blacklist:
						print(player)
						bing_url = 'https://www.bing.com/search?q={0}+pro+football+reference&qs=n&form=QBRE&sp=-1&ghc=2&pq={0}+pro+football+reference&sc=1-34&sk=&cvid=762A47430DA44F009A49EBF52BE60A5E'
						data = requests.get(bing_url.format(player.lower()),headers=headers)
						sleep(0.1)
						datadoc = lh.fromstring(data.content)
						element = datadoc.xpath('//h2')
						try:
							for k in element[0].xpath('//a'):
								pfr_url = k.attrib.get('href','')
								if 'https://www.pro-football-reference.com/players/' in pfr_url:
									data_pfr = requests.get(pfr_url,headers=headers)
									datadoc_pfr = lh.fromstring(data_pfr.content)
									elements_pfr_1 = datadoc_pfr.xpath('//span')
									for k in elements_pfr_1:
										eid = k.attrib.get('itemprop','')
										if eid == 'birthDate':
											players[player]['attrib']['dob'] = k.attrib.get('data-birth')
									break
						except Exception as e:
							print(e)
							print('Could not find results for player %s, blacklisting...' % player)
							blacklist.append(player)
					continue
				if yr not in players[player]['data']:
					players[player]['data'][yr] = {}
				players[player]['data'][yr][col_map[ix]] = float(t1.text_content().replace(',',''))
		sleep(1)
	
	with open(outfile,'w') as f:
		f.write(j.dumps(players))

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument('--position',type=str,default='rb')
	parser.add_argument('--outfile',type=str)
	
	FLAGS, unparsed = parser.parse_known_args()
	main(FLAGS.position,FLAGS.outfile)
	
