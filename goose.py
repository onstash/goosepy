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

def get_links(soup):
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

def get_comic(option):
	if option == "all":
		db = sqlite3.connect("links.sqlite")
		cursor = db.cursor()
		cursor.execute('SELECT comic_num,link from goose')
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
	elif option == "latest":
		db = sqlite3.connect("links.sqlite")
		cursor = db.cursor()
		cursor.execute('SELECT comic_num,link from goose WHERE comic_num=MAX(comic_num)')
		link = cursor.fetchone()
		dirr = os.getcwd()
		if not os.path.exists("Comics"):
			os.mkdir("Comics")
		os.chdir(dirr+'/Comics')
		comic_link = link[1]
		comic_num = link[0]
		download_comics(comic_num,comic_link)
		time.sleep(5)
		db.close()
	elif option == "range":
		db = sqlite3.connect("links.sqlite")
		cursor = db.cursor()
		
def first_run():
	os.mkdir("Comics")
	soup = get_soup(archive_url)
	get_links(soup)

def user_choice():
	print "\n\t\t\t\tWelcome to GoosePy v2.0a - AbstruseGoose comics downloader"
	print "\n"
	print "\t\t1.Download all comics"
	print "\t\t2.Download latest comic"
	print "\t\t3.Download a range of comics : 150-200"
	print "\t\t4.Exit"
	user_choice = input("\n\t\t\t\tEnter your choice : ")
	if user_choice == "1":
		get_comic("all")
	elif user_choice == "2":
		get_comic("latest")
	elif user_choice == "3":
		sys.exit("\nINVALID CHOICE!! EXITING!!")

def main():
	if not os.path.exists("links.sqlite"):
		first_run()
	user_choice()
	#get_links()


if __name__ == '__main__':
	main()