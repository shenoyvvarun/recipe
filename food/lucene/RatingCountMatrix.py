from UseritemRating import *

class RatingCountMatrix(object):
    """Rating count matrix used to find the similarity between two users or two items"""
    def __init__(self,user1_,user2_,dataset_,maxrating,user=True):
        self.matrix = [[0]*maxrating] *maxrating
        self.user1 = user1_
        self.user2 = user2_
        self.dataset = dataset_
        self._calculate(user)

    def _calculate(self,user):
        if user:
            a = set(self.dataset.getItemsForUser(self.user1))
            b = set(self.dataset.getItemsForUser(self.user2))
            self.intersection = a & b
            for item in self.intersection:
                ratingA = self.dataset(self.user1,item)-1
                ratingB = self.dataset(self.user2,item)-1
                self.matrix[ratingA][ratingB] +=1
        else:
            a = set(self.dataset.getUsersForItem(self.user1))
            b = set(self.dataset.getUsersForItem(self.user2))
            self.intersection = a & b
            for userI in self.intersection:
                ratingA = self.dataset(userI,self.user1)-1
                ratingB = self.dataset(userI,self.user2)-1
                self.matrix[ratingA][ratingB] +=1

    def get_totalcount(self):
        return len(self.intersection)

    def get_agreement_count(self):
        out=0
        i=0
        while i <len(self.matrix):
            out += self.matrix[i][i]
            i+=1
        return out
    
    def get_band_count(self,bandId):
        out = 0
        i = 0
        while i+bandId < len(self.matrix):
            out += self.matrix[i][i+bandId]
            out += self.matrix[i+bandId][i]
            i +=1
        return out

