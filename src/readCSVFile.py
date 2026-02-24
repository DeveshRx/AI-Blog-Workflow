import csv
from pydoc_data import topics


def getAllTopicsList():
    with open("./data/topics.csv", mode="r") as file:
        reader = csv.reader(file)
        topics=[]
        # topics = [row for row in reader]
        for row in reader:
            print(row)
            topics.append(row)
    return topics


#getAllTopicsList()