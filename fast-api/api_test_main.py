import json
from apimain import app
from fastapi.testclient import TestClient

client = TestClient(app)

trial_name = "Trial_Name"
trial_username = "trialusername"
trial_password = "trialpassword"
trial_plan = "Free"
trial_user_type = "Test"

payload = {'full_name': trial_name, 'username': trial_username, 'password': trial_password, 'plan': trial_plan, 'user_type': trial_user_type}
create_response = client.post("/user/create", json = payload)
login_response = client.post("/login", data = payload)
ACCESS_TOKEN = json.loads(login_response.text)["access_token"]

#Router: noaa-database, Endpoint 1
def test_geos_product():
    response = client.get("/noaa-database/goes18", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 1

#Router: noaa-database, Endpoint 2
def test_geos_years_product():
    response = client.get("/noaa-database/goes18/prod", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 2

#Router: noaa-database, Endpoint 3
def test_geos_invalid_years_product():
    response = client.get("/noaa-database/goes18/prod?product=xyz", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 404
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']

#Router: noaa-database, Endpoint 4
def test_geos_days_years():
    response = client.get(f"/noaa-database/goes18/prod/year?year=2022", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert json_resp[0] == '209'
    assert len(json_resp) == 154

#Router: noaa-database, Endpoint 5
def test_geos_hours_days():
    response = client.get("/noaa-database/goes18/prod/year/day?day=209&year=2022", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 24

#Router: noaa-database, Endpoint 6
def test_nexrad_years():
    response = client.get("/noaa-database/nexrad", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert json_resp == ['2022', '2023']

#Router: noaa-database, Endpoint 7
def test_nexrad_months_years():
    response = client.get("/noaa-database/nexrad/year?year=2022", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 12

#Router: noaa-database, Endpoint 8
def test_nexrad_invalid_months_years():
    response = client.get("/noaa-database/nexrad/year?year=2021", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 404
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']

#Router: noaa-database, Endpoint 9
def test_nexrad_days_months():
    response = client.get("/noaa-database/nexrad/year/month?month=01&year=2022", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 31

#Router: noaa-database, Endpoint 10
def test_nexrad_invalid_days_months():
    response = client.get("/noaa-database/nexrad/year/month?month=01&year=2021", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 404
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']

#Router: noaa-database, Endpoint 11
def test_get_stations_for_day_nexrad():
    response = client.get("/noaa-database/nexrad/year/month/day?day=01&month=01&year=2022", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 202

#Router: noaa-database, Endpoint 12
def test_nexrad_mapdata():
    response = client.get("/noaa-database/mapdata")
    assert response.status_code == 401

#Router: aws-s3-files, Endpoint 1
def test_list_files_in_goes18_bucket():
    response = client.get("/aws-s3-files/goes18?year=2022&day=209&hour=00&product=ABI-L1b-RadC", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 192

#Router: aws-s3-files, Endpoint 2
def test_list_files_in_goes18_bucket_invalid():
    response = client.get("/aws-s3-files/goes18?year=2022&day=209&hour=25&product=ABI-L1b-RadC", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 404
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']

#Router: aws-s3-files, Endpoint 3
def test_list_files_in_nexrad_bucket():
    response = client.get("/aws-s3-files/nexrad?year=2022&month=01&day=01&ground_station=FOP1", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 249

#Router: aws-s3-files, Endpoint 4
def test_list_files_in_nexrad_bucket_invalid():
    response = client.get("/aws-s3-files/nexrad?year=2022&month=00&day=01&ground_station=FOP1", headers={'Authorization' : f"Bearer {ACCESS_TOKEN}"})
    assert response.status_code == 404
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']

#Router: aws-s3-files, Endpoint 5
def test_copy_goes_file_to_user_bucket_invalid():
    response = client.post("/aws-s3-files/goes18/copyfile?file_name=invalidfile&product=ABI-L1b-RadC&year=2022&day=209&hour=00")
    assert response.status_code == 401

#Router: aws-s3-files, Endpoint 6
def test_copy_nexrad_file_to_user_bucket_invalid():
    response = client.post("/aws-s3-files/nexrad/copyfile?file_name=invalidfile&year=2022&month=01&day=01&ground_station=FOP1")
    assert response.status_code == 401

#Router: fetch_file, Endpoint 1
def test_generate_goes_url_invalid():
    response = client.post("/aws-s3-fetchfile/goes18?file_name=OR_ABI-L1b-Rad-M6C01_G18_s20222090001140_e20222090003513_c20222090003553.nc")
    assert response.status_code == 401

#Router: fetch_file, Endpoint 2
def test_generate_nexrad_url_invalid():
    response = client.post("/aws-s3-fetchfile/nexrad?file_name=FOP120220101_00206_V06")
    assert response.status_code == 401