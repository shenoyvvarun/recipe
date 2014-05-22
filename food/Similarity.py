from UseritemRating import UserItemRating
from RatingCountMatrix import RatingCountMatrix
from extract_recipe import Recipe
import cPickle
from fuzzywuzzy import fuzz
from fp_growth import find_frequent_itemsets
import urllib
import time

class UserSimilarity:
    def __init__(self,dataset_,rating_):
        self.dataset = dataset_
        self.similarityMatrix = dict()
        self.ratingvalue = rating_
        for user in self.dataset.users:
            self.similarityMatrix[user] = dict()
        self.calculate()

    def calculate(self):
        i = 0
        max = (len(self.dataset.users)*(len(self.dataset.users)+1))/2
        for u in self.dataset.users:
            for v in self.dataset.users:
                print i,"/",max
                if u==v:
                    self.similarityMatrix[u][v] = 1.0
                #do not recompute already computed similarity
                elif ((u in self.similarityMatrix) and (v in self.similarityMatrix[u])) or ((v in self.similarityMatrix) and (u in self.similarityMatrix[v])):
                    continue
                else:
                    rcm = RatingCountMatrix(u,v,self.dataset,self.ratingvalue)
                    total = rcm.get_totalcount()
                    agreement_count = rcm.get_agreement_count()
                    if total > 0:
                        self.similarityMatrix[u][v] = agreement_count/total
                    else:
                        self.similarityMatrix[u][v] = 0
                i+=1
        print "Similarity matrix construted"

    def __call__(self,user1,user2):
        if (user1 in self.similarityMatrix) and (user2 in self.similarityMatrix[user1]):
            return self.similarityMatrix[user1][user2]
        return self.similarityMatrix[user2][user1]

class ItemSimiliarity(object):
    def __init__(self,dataset_,rating_):
        self.dataset = dataset_
        self.similarityMatrix = dict()
        self.ratingvalue = rating_
        for item in self.dataset.recipes:
            self.similarityMatrix[item] = dict()
        self.calculate()

    def calculate(self):
        i = 0
        max = (len(self.dataset.recipes)*(len(self.dataset.recipes)+1))/2
        for u in self.dataset.recipes:
            for v in self.dataset.recipes:
                print i,"/",max
                if u==v:
                    self.similarityMatrix[u][v] = 1.0
                #do not recompute already computed similarity
                elif ((u in self.similarityMatrix) and (v in self.similarityMatrix[u])) or ((v in self.similarityMatrix) and (u in self.similarityMatrix[v])):
                    continue
                else:
                    rcm = RatingCountMatrix(u,v,self.dataset,self.ratingvalue,False)
                    total = rcm.get_totalcount()
                    agreement_count = rcm.get_agreement_count()
                    if total > 0:
                        self.similarityMatrix[u][v] = agreement_count/total
                    else:
                        self.similarityMatrix[u][v] = 0
                i+=1
        print "Similarity matrix construted"

    def __call__(self,item1,item2):
        if (item1 in self.similarityMatrix) and (item2 in self.similarityMatrix[item1]):
            return self.similarityMatrix[item1][item2]
        return self.similarityMatrix[item2][item1]

class PredictedRating(object):
    def __init__(self,user,item,rating):
        self.user = user
        self.item = item
        self.rating = rating

class Type(object):
    USER_BASED = 0
    ITEM_BASED = 1
    CONTENT_BASED = 2

class Recommendation(object):
    def __init__(self,dataset_,type):
        self.dataset = dataset_
        if type == Type.USER_BASED:
            self.similarity = UserSimilarity(self.dataset,5)
        elif type == Type.ITEM_BASED:
            self.similarity = ItemSimiliarity(self.dataset,5)
        elif type == Type.CONTENT_BASED:
            self.similarity = ContentSimilarity(self.dataset)
        self.type = type

    def recommend(self,user,n):
        recommendations = []
        if user not in dataset.users:
            return []
        for item in self.dataset.recipes:
            if self.dataset(user,item) == None:
                if self.type == Type.USER_BASED:
                    predictedRating = predictRating(user,item,Type.USER_BASED,self.dataset,self.usersimilarity)
                elif self.type == Type.ITEM_BASED:
                    predictedRating = predictRating(user,item,Type.ITEM_BASED,self.dataset,self.similarity)
                elif self.type == Type.CONTENT_BASED:
                    predictedRating = predictRating(user,item,Type.CONTENT_BASED,self.dataset,self.similarity)
                recommendations.append(PredictedRating(user,item,predictedRating))
        recommendations.sort(key=lambda x: x.rating, reverse=True)
        return [x.item for x in recommendations[:n]]

    def setdataset(self,dataset):
        self.dataset = dataset


def predictRating(user,item,method,dataset,similaritymatrix):
    if method == Type.USER_BASED:
        return estimateUserBasedRating(user,item,dataset,similaritymatrix)
    elif method == Type.ITEM_BASED:
        return estimateItemBasedRating(user,item,dataset,similaritymatrix)
    elif method == Type.CONTENT_BASED:
        return estimateContentBasedRating(user,item,dataset,similaritymatrix)

def estimateItemBasedRating(user,item,dataset,similaritymatrix):
    weightedsum =0
    similaritysum =0
    if dataset(user,item) != None:
        return dataset(user,item)
    for item1 in dataset.getItemsForUser(user):
        if dataset(user,item1) != None:
            similarity = similaritymatrix(item,item1)
            rating = dataset(user,item1)
            weightedsum += (similarity * rating)
            similaritysum += similarity
    if similaritysum > 0:
         return weightedsum/similaritysum
    return 0

def estimateUserBasedRating(user,item,dataset,similaritymatrix):
    weightedsum =0
    similaritysum =0
    for user1 in dataset.users:
        if dataset(user1,item) != None:
            similarity = similaritymatrix(user,user1)
            rating = dataset(user1,item)
            weightedsum += (similarity * rating)
            similaritysum += similarity
    if similaritysum > 0:
         return weightedsum/similaritysum
    return 0

def estimateContentBasedRating(user,item,dataset,similaritymatrix):
    weightedsum =0
    similaritysum =0
    for item1 in dataset.getItemsForUser(user):
        if dataset(user,item1) != None:
            similarity = similaritymatrix(item,item1)
            rating = dataset(user,item1)
            weightedsum += (similarity * rating)
            similaritysum += similarity
    if similaritysum > 0:
         return weightedsum
    return 0


def has_ing(ing,items):
    for i in items:
        if fuzz.partial_ratio(ing,i) > 80:
            return True
    return False

class ContentSimilarity(object):
    def __init__(self,dataset):
        self.dataset = dataset
        self.calculate()

    def similarity(self,item1,item2,obj):
        ing1 = self.dataset.recipes_ingredients[item1]
        ing2 = self.dataset.recipes_ingredients[item2]
        return float(len(set(ing1) & set(ing2)))/float(len(set(ing1) | set(ing2)))

    def calculate(self):
        self.similarityMatrix = dict()
        for item in self.dataset.recipes:
            self.similarityMatrix[item] = dict()
        obj = cPickle.load(open("output.pkl"))
        for u in dataset.recipes:
            for v in dataset.recipes:
                if u==v:
                    self.similarityMatrix[u][v] = 1.0
                #do not recompute already computed similarity
                elif ((u in self.similarityMatrix) and (v in self.similarityMatrix[u])) or ((v in self.similarityMatrix) and (u in self.similarityMatrix[v])):
                    continue
                else:
                    try:
                        self.similarityMatrix[u][v] = self.similarity(u,v,obj)
                    except ZeroDivisionError as e:
                        self.similarityMatrix[u][v] = 0

    def __call__(self,item1,item2):
        if (item1 in self.similarityMatrix) and (item2 in self.similarityMatrix[item1]):
            return self.similarityMatrix[item1][item2]
        return self.similarityMatrix[item2][item1]

#dataset = UserItemRating("output.pkl")
#dataset._calc_matrix()

#df = open("dataset.pkl","w")
#cPickle.dump(dataset,df)
#df.close()

dataset = cPickle.load(open("dataset.pkl"))
#r = Recommendation(dataset,Type.CONTENT_BASED)
#f = open("similCont.pkl","w")
#cPickle.dump(r,f)
#f.close()

#dataset = cPickle.load(open("dataset.pkl"))

##r = cPickle.load(open("similUser.pkl"))
#import time
#start = time.time()
#print r.recommend("crawfish pie",6)
#print time.time()-start
#print dataset.getItemsForUser("crawfish pie")


def recommend_recipes(user,n):
    
    if user not in dataset.users:
        ret = [("Bourbon Chicken","http://pictures.food.com/api/file/a2ZX1DphTjK0YuAi916b-149-bourbon-chicken.jpg"),("To Die for Crock Pot Roast","http://img.food.com/img/recipes/27/20/8/large/picVfzLZo.jpg"),("Crock-Pot Chicken With Black Beans & Cream Cheese","http://img.food.com/img/recipes/89/20/4/large/picec1bG3.jpg"),("Creamy Cajun Chicken Pasta","http://img.food.com/img/recipes/39/08/7/large/piccZDaro.jpg"),("\"Whatever Floats Your Boat\" Brownies!","http://img.food.com/img/recipes/32/20/4/large/picblOl7e.jpg"),("Best Ever Banana Cake With Cream Cheese Frosting","http://img.food.com/img/recipes/67/25/6/large/pichIPBA2.jpg"),("Pancakes","http://img.food.com/img/recipes/25/69/0/large/piciUoO07.jpg")]
        return ret[:n]
    item = cPickle.load(open("similItem.pkl"))
    item.setdataset(dataset)
    items = item.recommend(user,n+1)

    cont = cPickle.load(open("similCont.pkl"))
    cont.setdataset(dataset)
    conts  = cont.recommend(user,n+1)

    recipes = dataset.getItemsForUser(user)

    alpha = 5 * (n/2)
    transactions = []
    for recipe in recipes:
        transactions.append(dataset.recipes_ingredients[recipe] * dataset.matrix[user][recipe])
    f = find_frequent_itemsets(transactions,alpha)
    freq = []
    for i in f:
        if len(freq) >= n-1:
            break
        freq.append(i)
    out = conts[:len(freq)+1]
    out.extend(items)
    ret = []
    i=0
    while len(ret) < n:
        try:
            ret.append((out[i],dataset.imgs[out[i]]))
        except Exception:
            continue;
        i+=1  
    return ret

def get_recipe(recipe):
    ret = []
    ret.append(",".join(dataset.cat[recipe]))
    ret.append(dataset.imgs[recipe])
    ingred = "<ul>"
    for i in dataset.recipes_ingredients[recipe]:
        ingred += "<li>"+i+"</li>"
    ingred += "</ul>"
    ret.append(ingred)
    method = "<ol>"
    for i in dataset.recipe_method[recipe]:
        method += "<li>"+i+"</li>"
    method +="<ol>"
    ret.append(method)
    return ret
def rchop(thestring, ending):
  if thestring.endswith(ending):
    return thestring[:-len(ending)]
  return thestring

def get_search(out):
    if "" in out:
        out.remove("")
    html_out = "<table border='1'>"
    div = '<tr><td style="padding:10px"><img style="text-align:center" src="%s" height="100"/></td><td><h4><a href="recipeGen.py?recipe=%s">%s</a></h4><span>%s</span></td></tr>'
    for result in out:
        ret = []
        result = result.split("\\")
        recipe = result[-1]
        recipe = rchop(recipe,".html\r")
        ret.append(dataset.imgs[recipe])
        ret.append(urllib.quote(recipe))
        ret.append(recipe)
        ret.append(", ".join(dataset.cat[recipe]))
        html_out += div %tuple(ret)
    return html_out+"</table><br/><br/><br/>"

def saveRating(user,item,rating):
    dataset.addreview(user,item,rating)
    df = open("dataset.pkl","w")
    cPickle.dump(dataset,df)
    df.close()
    return "Your response has been recorded"

#dataset.addreview("varun","Peppered Buffalo Ranch Shrimp Pizza #RSC",5)
#dataset.addreview("varun","Pizza Dough and Sauce",5)
#dataset.addreview("varun","Banana Pancakes",5)
#dataset.addreview("varun","Fluffy Pancakes",5)
#dataset.addreview("varun","Zucchini Pancakes",5)

#dataset.addreview("varun","Bbq Chicken Pizza",5)
#dataset.addreview("varun","Pizza Hut Style Pizza Dough (Bread Machine)",5)
#dataset.addreview("varun","White Pizza or Pizza Blanca",5)
#get_search(["1. D:\\Apache\\cgi-bin\\food\\lucene\\indexHTML\\Palak Paneer (Indian Fresh Spinach With Paneer Cheese).html\r"])
#print recommend_recipes("varun",5)
#print dataset.getItemsForUser("varun")
