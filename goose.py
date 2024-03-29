import urllib
from bs4 import BeautifulSoup as Soup
import time
import os
import sqlite3
import sys
import lxml

archive_url = "http://abstrusegoose.com/archive"

def get_soup(archive_url):
	try:
		page = urllib.urlopen(archive_url).read()
	except Exception, e:
		sys.exit("There seems to be some connectivity issue with your Internet connection.")
	soup = Soup(page,"lxml")
	return soup

def get_links_from(soup):
	links = list()
	temp = soup.find_all('a')[2:-9]
	for link in temp:
		temp1 = link.get('href')
		if temp1 not in links:
			links.append(temp1)

	check_db(links)

def check_db(links):
	create_db()
	update_db2(links)

def create_db():
	db = sqlite3.connect("links.sqlite")
	cursor = db.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS goose(comic_num INTEGER PRIMARY KEY,link TEXT)")
	db.commit()
	db.close()

def update_db2(links):
	try:
		db = sqlite3.connect("links.sqlite")
		cursor = db.cursor()
		comics = list()
		for link in links:
			num = link[len("http://abstrusegoose.com/"):]
			num = int(num)
			comics.append((num,link))
		cursor.executemany('''INSERT INTO goose(comic_num,link) VALUES(?,?)''',comics)
		db.commit()
		db.close()
	except Exception, e:
		db.rollback()

def download_comics(comic_num,comic_link):
	try:
		comic = urllib.urlopen(comic_link).read()
	except Exception:
		sys.exit('\t\t\tThere seems to be a problem with the internet connection')
	
	comic_soup = Soup(comic,"lxml")
	comic_image_link = comic_soup.find_all('img')[1].get('src')
	comic_file_name = str(comic_num) + "_" + comic_soup.find_all('img')[1].get('src')[len('http://abstrusegoose.com/strips/'):]

	try:
		image = urllib.urlopen(comic_image_link).read()
	except Exception:
		sys.exit('\t\t\tThere seems to be a problem with the internet connection')

	if not os.path.exists(comic_file_name):
		f = open(comic_file_name,"w")
		f.write(image)
		f.close()
		print "\t" + comic_file_name + "\t-saved successfully"
	else:
		print "\t" + comic_file_name + "\t-SKIPPED because FILE ALREADY EXISTS"

def get_links():

	print "\tPyGoose v2.0 - AbstruseGoose comic downloader"
	print "\n1.Download all comics"
	print "2.Download latest comic"
	print "3.Download a range of comics - for example 150-200"
	user_choice = input('Enter your choice : ')
	user_choice = str(user_choice)
	if user_choice == "1":
		db = sqlite3.connect("links.sqlite")
		cursor = db.cursor()
		cursor.execute('SELECT comic_num,link FROM goose')
		links= list()
		links = cursor.fetchall()
		dirr = os.getcwd()
		if not os.path.exists("Comics"):
			os.mkdir("Comics")
		os.chdir(dirr+'/Comics')
		for link in links:
			comic_link = link[1]
			comic_num = link[0]
			download_comics(comic_num,comic_link)
			time.sleep(5)
		db.close()
	elif user_choice == "2":
		db = sqlite3.connect("links.sqlite")
		cursor = db.cursor()
		cursor.execute('SELECT MAX(comic_num),link FROM goose')
		link = cursor.fetchone()
		dirr = os.getcwd()
		if not os.path.exists("Comics"):
			os.mkdir("Comics")
		os.chdir(dirr+'/Comics')
		comic_num = link[0]
		comic_link = link[1]
		download_comics(comic_num,comic_link)
		time.sleep(5)
		db.close()
	elif user_choice=="3":
		sys.exit("\nBYE.")
		db = sqlite3.connect("links.sqlite")
		cursor = db.cursor()
		min_range = input('Enter min_range : ')
		max_range = input('Enter max_range : ')
		min_range = int(min_range)
		max_range = int(max_range)
		links = list()
		for i in range(min_range,max_range+1):
			cursor.execute('SELECT * FROM goose WHERE comic_num = ? ',(i,))
			link = cursor.fetchone()
			comic_num = link[0]
			comic_link = link[1]
			download_comics(comic_num,comic_link)
			time.sleep(5)
		db.close()
def first_run():
	os.mkdir("Comics")
	soup = get_soup(archive_url)
	get_links_from(soup)


def main():
	if not os.path.exists("links.sqlite"):
		first_run()
	get_links()


if __name__ == '__main__':
	main()