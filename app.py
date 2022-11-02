from cProfile import label
from operator import index
from flask import *
import pandas as pd
import config
#from transformers import AutoTokenizer
import json
# from model import model_infer
#import torch
from statistics import mean, stdev, variance

firebase = config.connection()
app = Flask(__name__)
app.secret_key = "Abcd1234"

# tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", use_fast=False)
# model = model_infer.SentimentClassifier()
# model.load_state_dict(torch.load(f'package\last_step.pth',map_location=torch.device('cpu')))
# model.eval()
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def save_df(df, id):
    postdata = df.to_dict()
    result = firebase.put("/input", id, postdata)
    return result


def create_new(df):
    df2 = pd.DataFrame()
    df2["review"] = df["Review"]
    df2["place_id"] = df["country"]
    df2["entertainment"] = df["giai_tri"]
    df2["accommodation"] = df["luu_tru"]
    df2["restaurant_serving"] = df["nha_hang"]
    df2["food"] = df["an_uong"]
    df2["traveling"] = df["di_chuyen"]
    df2["shopping"] = df["mua_sam"]
    df2["status"] = False
    grouped = df2.groupby(df2.place_id)
    country_code = df2["place_id"].to_list()
    country_code = list(set(country_code))
    for i in country_code:
        df_new = grouped.get_group(int(i))
        save_df(df_new, i)
    # postdata = df2.to_dict()
    # result = firebase.post('/input', postdata, {'print': 'pretty'})
    return True


def query(page, typ_inp):
    val = firebase.get("/input/" + str(page), typ_inp)
    return val


def get_value_by_status(dic, status):
    temp = []
    for x, y in dic.items():
        if x not in status:
            temp.append(y)
    return temp


def save_cal(page, an_uong_cal, di_chuyen_cal, giai_tri, luu_tru, mua_sam, nha_hang):
    dict_save = {
        "mean":{
            "food" : mean(an_uong_cal),
            "traveling": mean(di_chuyen_cal),
            "entertainment" : mean(giai_tri),
            "accommodation" : mean(luu_tru),
            "shopping" : mean(mua_sam),
            "restaurant_serving" : mean(nha_hang)
        },
        "std":{
            "food" : stdev(an_uong_cal),
            "traveling": stdev(di_chuyen_cal),
            "entertainment" : stdev(giai_tri),
            "accommodation" : stdev(luu_tru),
            "shopping" : stdev(mua_sam),
            "restaurant_serving" : stdev(nha_hang)
        },
        "var":{
            "food" : variance(an_uong_cal),
            "traveling": variance(di_chuyen_cal),
            "entertainment" : variance(giai_tri),
            "accommodation" : variance(luu_tru),
            "shopping" : variance(mua_sam),
            "restaurant_serving" : variance(nha_hang)
        },
    }
    result = firebase.put("/cal", page, dict_save)

@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/confirm", methods=["POST"])
def upload():
    file = request.files["file"]
    if file:
        df = pd.read_csv(file, index_col=False)
        df.drop('Unnamed: 0', inplace=True, axis=1)

        res = create_new(df)
        if res:
            return render_template("csv_table.html", tables=[df.to_html(header=False)])
    flash("fail")
    return render_template("index.html")


@app.route("/cal", methods=["GET"])
def cal():
    print("loading")
    status = []
    an_uong = []
    di_chuyen = []
    giai_tri = []
    luu_tru = []
    mua_sam = []
    nha_hang = []
    # test = firebase.get('/input/1/Review',2)
    # print(test)
    for i in range(1, 6):
        boo_val = query(i, "status")
        for x, y in boo_val.items():
            if y == True:
                status.append(x)
        an_uong = get_value_by_status(query(i, "food"), status)
        di_chuyen = get_value_by_status(query(i, "traveling"), status)
        giai_tri = get_value_by_status(query(i, "entertainment"), status)
        luu_tru = get_value_by_status(query(i, "accommodation"), status)
        mua_sam = get_value_by_status(query(i, "shopping"), status)
        nha_hang = get_value_by_status(query(i, "restaurant_serving"), status)
        save_cal(i, an_uong, di_chuyen, giai_tri, luu_tru, mua_sam, nha_hang)
    return "Complete the calculation and send the data to the server!!!"


if __name__ == "__main__":
    app.run(debug=True)
