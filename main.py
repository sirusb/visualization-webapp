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
    """
    returns statistics about all the 45 willayas
    """
    res = requests.get("https://stats-api.covid19dz.com/wilayas")   
    if res.status_code != 200 :
        msg = { "error" : "Couldn't fetch the data"}
        return msg, res.status_code        
    return res.json()

@app.get("/confirmed/wilaya")
def wilayaWithConfirmedCases():
    """
    returns statistics only about willayas with confirmed cases
    """
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
    """
    returns statistics only about willayas who still have hospitalized people
    """
    res = requests.get("https://stats-api.covid19dz.com/wilayas")   
    if res.status_code != 200 :
        msg = { "error" : "Couldn't fetch the data"}
        return msg, res.status_code    

    wilaya = res.json()
    # Return just the list of infected wilaya
    infected = [ { 'name' : x['name'], 'name_ar' : x['name_ar'], 'actives': x['actives'] } for x in wilaya if x['actives'] ]    

    # sort by the number of infected people
    infected = sorted(infected, key = lambda x: x['actives'], reverse=False) 
    return infected


@app.get("/origins")
def casesOrigins():
    """
    Returns the distribition of cases by origine, basically just calles the stats-api.covid19dz.com
    This function can be deleted in the future if no additional logic is added.
    """
    res = requests.get("https://stats-api.covid19dz.com/origins")
    if res.status_code != 200 :
        msg = { "error" : "Couldn't fetch the data"}
        return msg, res.status_code     

    return res.json()


@app.get("/ages")
def agesdistribution():
    """
    Returns statistics about the number of infected people by agao category    
    """
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
        
    return info2

@app.get("/sex")
def casesOrigines():
    """
    Returns the distribition of cases by sex, basically just calles the stats-api.covid19dz.com
    This function can be deleted in the future if no additional logic is added.
    """
    res = requests.get("https://stats-api.covid19dz.com/sex")
    if res.status_code != 200:
        msg = { "error" : "Couldn't fetch the data"}
        return msg, res.status_code  
    
    return res.json()