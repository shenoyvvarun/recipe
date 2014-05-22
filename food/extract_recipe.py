#!/var/lib/openshift/537e1a3c5973cadc06000a62/app-root/data/bin/python
#from requests import session
#from lxml import html
import threading
#import threadpool
import re
import cPickle

class Recipe(object):
    def __init__(self,title_,ingredients_,reviews_,imgurl_,cats,method):
        self.title = title_
        self.ingredients = ingredients_
        self.reviews = reviews_
        self.imgurl = imgurl_
        self.cats = cats
        self.method = method

def get_html_for_url(url):
    resp = food_session.get(url)
    if resp.status_code != 200:
        return None
    return resp.text

def extract_review_from_tree(tree):
    reviews  = tree.xpath('//ul[@id="rating_review_list_ul"]/li')
    out = []
    for review in reviews:
        rating = review.xpath('.//div/div/p/span/@class')
        name = review.xpath('.//div/div/div/p/a')[0].text_content()
        name = name.strip()
        if len(rating) != 0:
            rating  = int(rating[0].strip()[-1])
            out.append((name,rating))
    return out

def extract_review(url):
    html_text = get_html_for_url(url)
    out = []
    if html_text != None:
        tree = html.fromstring(html_text)
        #get the page number
        num = tree.xpath('//div[@id="rz-w"]/div[@class="rz-pagi"]/a/@href')
        if len(num) != 0:
            temp_num = [int((x.split("=")[-1]).strip()) for x in num]
            num = max(temp_num)
        else:
            num = 2
        #get 1st page data
        res = extract_review_from_tree(tree)
        out.extend(res)
        for i in range(2,num+1):
            html_text = get_html_for_url(url+"?pn="+str(i))
            tree = html.fromstring(html_text)
            res = extract_review_from_tree(tree)
            out.extend(res)
    return out

def extract_data(url):
    global count,pool
    html_text = get_html_for_url(url)
    if html_text != None:
        tree = html.fromstring(html_text)
        title = re.sub(r"(\n|\t|\s)+", " ",tree.xpath("//div[@id='rz-lead']/div/span/h1")[0].text_content()).strip()
        ingredients_name = []
        ingredients = tree.xpath('//div[@class="pod ingredients"]/ul/li/span/span[@class="name"]')
        for ingredient in ingredients:
            name = ingredient.xpath("/a")
            if len(name)==0:
                name = ingredient
            name = name.text_content()
            name = re.sub(r"(\n|\t|\s)+", " ", name).strip()
            ingredients_name.append(name)
        imgurl = tree.xpath('//div[@id="enlrphoto"]/img/@src')
        if len(imgurl) == 0:
            imgurl =None
        else:
            imgurl = str(imgurl[0])
        cats = tree.xpath('//p[@class="recipe-cats"]/a/span')
        cats.extend(tree.xpath('//div[@class="more-tags"]/div[@class="bd"]/ul/li/a/span'))
        cats = [x.text_content() for x in cats]
        if "" in cats:
            cats.remove("")
        method = tree.xpath('//span[@itemprop="recipeInstructions"]/ol/li/div[@class="txt"]')
        method = [x.text_content().encode('utf8') for x in method]
        if "" in method:
            method.remove("")

    if html_text!= None:
        out = extract_review(url+"/review")
        output_lock.acquire()
        output_list.append(Recipe(title,ingredients_name,out,imgurl,cats,method))
        output_lock.release()
        count +=1
        print count,"/",pool._requests_queue.qsize()

#def start():
if __name__=="__main__":
    count =0
    payload = {
         'username': 'varunfriend@gmail.com',
         'password': 'Munni123&',
         'SMSAVECREDS':'YES',
         'login':"Log+In",
         'pwdtext': 'Munni123&',
         'callbackurl': "/static_files/communitytools/empty.html",
         'callbackUrl': "/static_files/communitytools/empty.html",
     }

    food_session = session()
    food_session.post("https://mysecure.food.com/aim/rest/login",data=payload)
    output_list = []
    output_lock =  threading.Lock()
    data = open("urls.txt").read().strip().split()
    pool = threadpool.ThreadPool(100)
    requests = threadpool.makeRequests(extract_data,args_list=data)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    f = open("output.pkl","w")
    cPickle.dump(output_list,f)
    f.close()
