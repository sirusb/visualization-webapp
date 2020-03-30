# -*- coding: utf-8 -*-

import requests
import re
from fastapi import FastAPI


app = FastAPI(
    title="DZ COVID-19 Visualization app",
    description="A RESTful back-end API for the visualization app",
    version="0.0.9",
)




#I feel this is a duplicated method
#I just wrote it because the Access-Control-Allow-Origin problem
@app.get("/history")
def history():
    """
    Return historical statistics    
    """
    req = requests.get("https://stats-api.covid19dz.com/v2/history")    
    if req.statlsus_code != 200 :
        msg = { "error" : "Couldn't fetch the data"}
        return msg, req.status_code    
        
    alg_info = req.json()    

    cases = [ (x['date'] , x['confirmed'] if not x['confirmed'] is None else 0) for x in alg_info if 'confirmed' in x]
    deaths = [(x['date'] , x['deaths'] if not x['deaths'] is None else 0) for x in alg_info if 'deaths' in x ]
    recovered = [ (x['date'] ,  x['recovered'] if not x['recovered'] is None  else 0) for x in alg_info]
    cases = cases[:-1]
    deaths = deaths[:-1]
    recovered = recovered[:-1]
    res = {
        'cases': dict(cases),
        "deaths": dict(deaths),
        "recovered": dict(recovered),
        'stats': {
            # I am suposing it is sorted            
            "Total" : cases[-1][1],
            "Deaths": deaths[-1][1],
            "Recovered": recovered[-1][1],
            "NewCases": cases[-1][1] - cases[-2][1],
            "StillInfected": cases[-1][1] - ( deaths[-1][1] + recovered[-1][1] )  
        }
    }    
    return res

@app.get("/allWilayasStats")
def allWilayasStats():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    res = requests.get("https://stats-api.covid19dz.com/wilayas")   
    if res.status_code != 200 :
        msg = { "error" : "Couldn't fetch the data"}
        return msg, res.status_code        
    return res.json()

@app.get("/confirmed/wilaya")
def wilayaWithConfirmedCases():
    # I will 
    res = requests.get("https://stats-api.covid19dz.com/wilayas")   
    if res.status_code != 200 :
        msg = { "error" : "Couldn't fetch the data"}
        return msg, res.status_code     

    wilaya = res.json()
    filtered = [x for x in wilaya if x['confirmed'] >0 ]   
    filtered = sorted(filtered, key = lambda x: x['confirmed'], reverse=False)  
    return filtered


@app.get("/active/wilaya")    
def stillInfectedWilaya():
    res = requests.get("https://stats-api.covid19dz.com/wilayas")   
    if res.status_code != 200 :
        msg = { "error" : "Couldn't fetch the data"}
        return msg, res.status_code    

    wilaya = res.json()
    # Return just the list of infected wilaya
    infected = [ { 'name' : x['name'], 'name_ar' : x['name_ar'], 'actives': x['actives'] } for x in wilaya if x['actives'] ]    

    # sort by the number of infected people
    infected = sorted(infected, key = lambda x: x['actives'], reverse=False) 
    return nfected


@app.get("/origins")
def casesOrigins():
    res = requests.get("https://stats-api.covid19dz.com/origins")
    if res.status_code != 200 :
        msg = { "error" : "Couldn't fetch the data"}
        return msg, res.status_code     

    return res.json()


@app.get("/ages")
def agesdistribution():
    res = requests.get("https://stats-api.covid19dz.com/ages")
    if res.status_code != 200 :
        msg = { "error" : "Couldn't fetch the data"}
        return msg, res.status_code  

    info = res.json()    
    # just substiture the -5 label with <5 label

    info2 = {}
    for cat in list(info):        
        cat_fixes = re.sub("^-","0-",cat)
        cat_fixes = re.sub("^\+70","70+",cat_fixes)
        info2[cat_fixes] = info[cat]    
    
    print(info2)
    return info2

@app.get("/sex")
def casesOrigines():
    res = requests.get("https://stats-api.covid19dz.com/sex")
    if res.status_code != 200:
        msg = { "error" : "Couldn't fetch the data"}
        return msg, res.status_code  
    
    return res.json()