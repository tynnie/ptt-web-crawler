#coding=utf-8 
import re
import sys
import json
import requests
import io
import random
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup  
requests.packages.urllib3.disable_warnings()

PttName=""
load={
'from':'/bbs/'+PttName+'/index.html',
'yes':'yes' 
}
cookies={'over18': '1'}
rs=requests.session()
res=rs.post('https://www.ptt.cc/ask/over18',verify=False,data=load)
FILENAME=""

def PageCount(PttName):
    res=rs.get('https://www.ptt.cc/bbs/'+PttName+'/index.html',verify=False)
    soup=BeautifulSoup(res.text,'html.parser')
    ALLpageURL = soup.select('.btn.wide')[1]['href']
    ALLpage=int(getPageNumber(ALLpageURL))+1
    return  ALLpage 

def crawler(PttName,ParsingPage):
        ALLpage=PageCount(PttName)
        g_id = 0;
        for number in range(ALLpage, ALLpage-int(ParsingPage), -1):
            res=rs.get('https://www.ptt.cc/bbs/'+PttName+'/index'+str(number)+'.html',verify=False)
            soup = BeautifulSoup(res.text,'html.parser')
            for tag in soup.select('div.title'):
                
                try:
                    atag=tag.find('a')
#                    time=random.uniform(0, 1)/5
#		                    #print 'time:',time
#                    sleep(time)
                    if(atag):
                        URL=atag['href']
                        link='https://www.ptt.cc' + URL
                        g_id = g_id+1
                        parseGos(link,g_id)
                except:
                    print('error:',URL)
 
def parseGos(link , g_id):
        res=rs.get(link,verify=False)
        soup = BeautifulSoup(res.text,'html.parser')
        try:
            author  = soup.select('.article-meta-value')[0].text
        
        except:
            author = "author is not find"
            
        try:
            title = soup.select('.article-meta-value')[2].text
        
        except:
            title = "title is not find"
        
        
        try:
            date = soup.select('.article-meta-value')[3].text
        
        except:
            date = "date is not find"

        
        
  
        try:
                targetIP=u'※ 發信站: 批踢踢實業坊'
                ip =  soup.find(string = re.compile(targetIP))
                ip = re.search(r"[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*",ip).group()
        except:
                ip = "ip is not find"

        try:
            content = soup.find(id="main-content").text
            target_content=u'※ 發信站: 批踢踢實業坊(ptt.cc),'
            content = content.split(target_content)
            content = content[0].split(date)
            main_content = content[1].replace('\n', '  ').replace('\t', '  ')
        except:
            content = "content is not find"
        
        try:
            num , g , b , n ,message = 0,0,0,0,{}
            for tag in soup.select('div.push'):
                    num += 1
                    push_tag = tag.find("span", {'class': 'push-tag'}).text
                    #print "push_tag:",push_tag
                    push_userid = tag.find("span", {'class': 'push-userid'}).text       
                    #print "push_userid:",push_userid
                    push_content = tag.find("span", {'class': 'push-content'}).text   
                    push_content = push_content[1:]
                    #print "push_content:",push_content
                    push_ipdatetime = tag.find("span", {'class': 'push-ipdatetime'}).text   
                    push_ipdatetime = remove(push_ipdatetime, '\n')
                    #print "push-ipdatetime:",push_ipdatetime 
                    
                    message[num]={"狀態":push_tag,"留言者":push_userid,
                                  "留言內容":push_content,"留言時間":push_ipdatetime}
                    if push_tag == u'推 ':
                        g += 1
                    elif push_tag == u'噓 ':
                        b += 1
                    else:
                        n += 1
            
            messageNum = {"g":g,"b":b,"n":n,"all":num}
        except:
            message[1]={"狀態":"None","留言者":"None",
                              "留言內容":"None","留言時間":"None"}
            messageNum = {"g":"None","b":"None","n":"None","all":"None"}
#        # json-data  type(d) dict
#          #.encode('utf-8')非必要
#        d={"a_ID":str(g_id) , "b_作者":author.encode('utf-8'), "c_標題":title.encode('utf-8'), "d_日期":date.encode('utf-8'),
#           "e_ip":ip.encode('utf-8'), "f_內文":main_content.encode('utf-8'), "g_推文":message,"h_推文總數":messageNum}
        d={"a_ID":str(g_id) , "b_作者":author, "c_標題":title, "d_日期":date,
           "e_ip":ip, "f_內文":main_content, "g_推文":message,"h_推文總數":messageNum}
        
        json_data = json.dumps(d,ensure_ascii=False, indent=4, sort_keys=True)+','
#        print(json_data)
        store(json_data) 

def store(data):
    with open(FILENAME, 'a') as f:
        f.write(data)
     
def remove(value, deletechars):
    for c in deletechars:
        value = value.replace(c,'')
    return value.rstrip();
   

def getPageNumber(content) :
    startIndex = content.find('index')
    endIndex = content.find('.html')
    pageNumber = content[startIndex+5 : endIndex]
    pageNumber = str(int(pageNumber) -1)
    return pageNumber

if __name__ == "__main__":  
   PttName = str(sys.argv[1])
   ParsingPage = int(sys.argv[2])
#   PttName = "HatePolitics"
#   ParsingPage = 3000
   FILENAME='data-'+PttName+'-'+datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+'.json'
   store('[') 
   print('Start parsing [',PttName,']....')
   crawler(PttName,ParsingPage)
   store(']') 
   

   with open(FILENAME, 'r', encoding='utf-8') as f:
        p = f.read()
   with open(FILENAME, 'w', encoding='utf-8') as f:
        #f.write(p.replace(',]',']'))
        f.write(p[:-2]+']')   
 
