import cPickle

class UserItemRating(object):
    """ For user i with item j, the rating of user i for item j is UserItemRating(i,j)"""
    def __init__(self,filename_):
        self.matrix = dict()
        self.filename = filename_
        self.users = set()
        self.recipes = set()
        self.recipes_ingredients=dict()
        self.cat = dict()
        self.recipe_method =dict()
        self.imgs=dict()

    def _calc_matrix(self):
        #unpickle the obj file
        obj = cPickle.load(open(self.filename))
        temp = dict()
        for recipe in obj:
            for users in recipe.reviews:
                if users[0] not in temp:
                    temp[users[0]] = 1
                else:
                    temp[users[0]]+=1
        it = temp.items()
        for k,v in it:
            if v == 1 :
                temp.pop(k)
        matrix = self.matrix
        print len(temp)
        #load users and items
        for recipe in obj:
            self.recipes.add(recipe.title)
            self.recipes_ingredients[recipe.title] = recipe.ingredients
            self.recipe_method[recipe.title] = recipe.method
            self.cat[recipe.title] = recipe.cats
            self.imgs[recipe.title] = recipe.imgurl
            for review in recipe.reviews:
                #check if the user exists
                if review[0] in temp:
                    self.users.add(review[0])
                    if review[0] not in matrix:
                        matrix[review[0]] = dict()
                    matrix[review[0]][recipe.title] = review[1]
        self.inverse(obj)

    def inverse(self,obj):
        self.inv_matrix = dict()
        for recipe in obj:
            self.inv_matrix[recipe.title] = set()
            for review in recipe.reviews:
                self.inv_matrix[recipe.title].add(review[0])

    def __call__(self,user,recipe):
        if (user in self.matrix) and (recipe in self.matrix[user]):
            return self.matrix[user][recipe]
        return None

    def save(self,file_):
        f = open(file_,"w")
        cPickle.dump(self,f)
        f.close()

    def load(self,file_):
        return cPickle.load(open(file_))

    def getItemsForUser(self,user):
        return self.matrix[user].keys()

    def getUsersForItem(self,item):
        return self.inv_matrix[item]

    def addreview(self,user,item,rating):
        if user not in self.matrix:
            self.matrix[user] = dict()
        self.matrix[user][item] = rating
        self.inv_matrix[item].add(user)
        self.users.add(user)

##a = UserItemRating("output.pkl")
##a._calc_matrix()
#a = UserItemRating("output.pkl").load("useritemRating.pkl")
#print a("cakebaker61","Bourbon Chicken")
#print a('MizzNezz', "To Die for Crock Pot Roast")
#print a("cakebaker61","To Die for Crock Pot Roast")
#print a("MizzNezz","Bourbon Chicken")
##a.save("useritemRating.pkl")
