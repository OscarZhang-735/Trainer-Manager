import crawler
import data
import json

import utils

if __name__ == '__main__':
    queryObj = crawler.Spider.Search("Grand")
    search_result = queryObj.run()
    print(search_result)
    new_dict = {
        "Name": search_result[0][0],
        "Link": search_result[0][1],
        "Image": search_result[0][2]
    }
    print(new_dict)
    data = utils.Data.json_read("data/data.json")
    data["Favor"]["Trainers"].append(new_dict)
    #data["Favor"]["Trainers"] = list(set(data["Favor"]["Trainers"]))
    utils.Data.json_write("data/data.json", data)

    detailObj = crawler.Spider.Download("https://flingtrainer.com/train/")
    download_result = detailObj.run()
    print(download_result)

