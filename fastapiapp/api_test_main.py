import json
import warnings
from .apimain import app
from fastapi.testclient import TestClient
warnings.filterwarnings('ignore')

API_URL = "http://localhost:8000"

client = TestClient(app)

test_full_name = "tryfullaname"
test_username = "tryusername"
test_password = "trypassword"
test_plan = "Free"
test_user_type = "Test"

#first generate token for test user
payload = {'full_name': test_full_name, 'username': test_username, 'password': test_password, 'plan': test_plan, 'user_type': test_user_type}
create_user_resp = client.post("/user/create", json=payload)
login_user_resp = client.post("/login", data=payload)
json_data = json.loads(login_user_resp.text)
ACCESS_TOKEN = json_data["access_token"]
header = {}
header['Authorization'] = f"Bearer {ACCESS_TOKEN}"

#Router: authenticate
def test_incorrect_login():
    payload={'username': 'nouser', 'password': 'incorrectpass'}
    response = client.post("/login", data=payload)
    assert response.status_code == 404

#Router: noaa-database, Endpoint 1
def test_get_product_goes():
    response = client.get("/noaa-database/goes18", headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 1  #only 1 product considered for GOES18 should be returned

#Router: noaa-database, Endpoint 2
def test_get_years_in_product_goes():
    response = client.get("/noaa-database/goes18/prod", headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 2  #only 2 years included in given default product

#Router: noaa-database, Endpoint 2
def test_get_years_in_product_goes_invalid():
    response = client.get("/noaa-database/goes18/prod?product=xyz", headers=header)
    assert response.status_code == 404
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']   #making sure the response has only 1 key which is "detail" (the detail of the HTTP exception occured)

#Router: noaa-database, Endpoint 3
def test_get_days_in_year_goes():
    response = client.get(f"/noaa-database/goes18/prod/year?year=2022", headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert json_resp[0] == '209' #first day listed in year 2022 is 209
    assert len(json_resp) == 154  #year 2022 has days listed from 209 to 365, meaning 154 days

#Router: noaa-database, Endpoint 4
def test_get_hours_in_day_goes():
    response = client.get("/noaa-database/goes18/prod/year/day?day=209&year=2022", headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 24  #all 24 hour data available

#Router: noaa-database, Endpoint 5
def test_get_years_nexrad():
    response = client.get("/noaa-database/nexrad", headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert json_resp == ['2022', '2023']  #only 2 years available in NEXRAD

#Router: noaa-database, Endpoint 6
def test_get_months_in_year_nexrad():
    response = client.get("/noaa-database/nexrad/year?year=2022", headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 12  #all 12 months data available in year 2022

#Router: noaa-database, Endpoint 6
def test_get_months_in_year_nexrad_invalid():
    response = client.get("/noaa-database/nexrad/year?year=2021", headers=header)
    assert response.status_code == 404  #no data available years other than 2022 and 2023
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']   #making sure the response has only 1 key which is "detail" (the detail of the HTTP exception occured)

#Router: noaa-database, Endpoint 7
def test_get_days_in_month_nexrad():
    response = client.get("/noaa-database/nexrad/year/month?month=01&year=2022", headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 31  #for Jan 2022, 31 days' data available

#Router: noaa-database, Endpoint 7
def test_get_days_in_month_nexrad_invalid():
    response = client.get("/noaa-database/nexrad/year/month?month=01&year=2021", headers=header)
    assert response.status_code == 404
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']   #making sure the response has only 1 key which is "detail" (the detail of the HTTP exception occured)

#Router: noaa-database, Endpoint 8
def test_get_stations_for_day_nexrad():
    response = client.get("/noaa-database/nexrad/year/month/day?day=01&month=01&year=2022", headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 202  #for 01 Jan 2022, 202 stations' data available

#Router: noaa-database, Endpoint 9
def test_get_nextrad_mapdata():
    response = client.get("/noaa-database/mapdata")
    assert response.status_code == 401 #since you are an unauthroized user with no authentication token

#Router: aws-s3-files, Endpoint 1
def test_list_files_in_goes18_bucket():
    response = client.get("/aws-s3-files/goes18?year=2022&day=209&hour=00&product=ABI-L1b-RadC", headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 192  #192 files at given selection folder

#Router: aws-s3-files, Endpoint 1
def test_list_files_in_goes18_bucket_invalid():
    response = client.get("/aws-s3-files/goes18?year=2022&day=209&hour=25&product=ABI-L1b-RadC", headers=header)
    assert response.status_code == 404  #hour 25 does not exist
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']   #making sure the response has only 1 key which is "detail" (the detail of the HTTP exception occured)

#Router: aws-s3-files, Endpoint 2
def test_list_files_in_nexrad_bucket():
    response = client.get("/aws-s3-files/nexrad?year=2022&month=01&day=01&ground_station=FOP1", headers=header)
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 249  #249 files at given selection folder

#Router: aws-s3-files, Endpoint 2
def test_list_files_in_nexrad_bucket_invalid():
    response = client.get("/aws-s3-files/nexrad?year=2022&month=00&day=01&ground_station=FOP1", headers=header)
    assert response.status_code == 404
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']

#Router: aws-s3-files, Endpoint 3
def test_copy_goes_file_to_user_bucket_invalid():
    response = client.post("/aws-s3-files/goes18/copyfile?file_name=invalidfile&product=ABI-L1b-RadC&year=2022&day=209&hour=00")
    assert response.status_code == 401

#Router: aws-s3-files, Endpoint 4
def test_copy_nexrad_file_to_user_bucket_invalid():
    response = client.post("/aws-s3-files/nexrad/copyfile?file_name=invalidfile&year=2022&month=01&day=01&ground_station=FOP1")
    assert response.status_code == 401

#Router: aws-s3-fetchfile, Endpoint 1
def test_generate_goes_url_invalid():
    response = client.post("/aws-s3-fetchfile/goes18?file_name=OR_ABI-L1b-Rad-M6C01_G18_s20222090001140_e20222090003513_c20222090003553.nc")
    assert response.status_code == 401

#Router: aws-s3-fetchfile, Endpoint 2
def test_generate_nexrad_url_invalid():
    response = client.post("/aws-s3-fetchfile/nexrad?file_name=FOP120220101_00206_V06")
    assert response.status_code == 401