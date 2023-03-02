import json
import typer
import requests
from dataclasses import dataclass

typercli = typer.Typer(add_completion=False)
BASE_URL = "http://localhost:8000"

@dataclass
class User:
    username: str
    password: str

@typercli.command()
def user_registration(ctx: typer.Context, full_name):
    if len(ctx.obj.password) < 6:
        typer.echo("Password should be minimum 6 characters long")
    elif full_name == '' or ctx.obj.username == '' or ctx.obj.password == '':
        typer.echo("Please fill all fields.")
    else:
        register_user = {'full_name': full_name, 'username': ctx.obj.username, 'password': ctx.obj.password}
        response = requests.post(url=f'{BASE_URL}/user/create', json=register_user)

        if response.status_code == 405:
            typer.echo(response.json())
        elif response and response.status_code == 200:
            access_token = response.json().get('access_token')
            typer.echo("Account is created successfully !!")
            typer.echo(f"Access Token is {access_token}")
            typer.echo("Now Please login to access the features !!!")

# Get Request # http://localhost:8000/aws-s3-files/goes18?year=2022&day=271&hour=06&product=ABI-L1b-RadC'
@typercli.command()
def aws_s3_files_geos18(ctx: typer.Context, product_input: str, year_input: str, day_input: str, hour_input: str):
    logged_in = False
    payload = {'username': ctx.obj.username, 'password': ctx.obj.password}
    response = requests.post(f"{BASE_URL}/login", data=payload)
    if response.status_code == 200:
        typer.echo("Logged in successfully as {}".format(ctx.obj.username))
        json_data = json.loads(response.text)
        logged_in = True
        access_token = json_data['access_token']
        typer.echo(f"Access Token is {access_token}")
    elif response.status_code == 401:
        typer.echo("Please Register First !!!")
    elif response.status_code == 405:
        typer.echo(response.json())  
    else:
        typer.echo("Incorrect Username or Password Entered !!!")

    if logged_in:
        try:
            response = requests.get(f"{BASE_URL}/aws-s3-files/goes18?year={year_input}&day={day_input}&hour={hour_input}&product={product_input}", headers={'Authorization': f'Bearer {access_token}'})
            if response.status_code == 200:
                json_data = json.loads(response.text)
                typer.echo(f"Files available in the bucket for {product_input}, {year_input}, {day_input}, {hour_input} are:")
                typer.echo(json_data)
            else:
                typer.echo(response.status_code)
        except requests.exceptions.HTTPError as httperr:
            if response.status_code == 401:
                typer.echo("Unauthorized: Invalid username or password")
            elif response.status_code == 403:
                typer.echo("Forbidden: You do not have permission to access this resource - Sign Back In!")
            else:
                typer.echo(f"HTTP error occurred: {httperr}")
        except requests.exceptions.RequestException as reqerr:
            typer.echo(f"An error occurred: {reqerr}")

# Post Request # http://localhost:8000/aws-s3-fetchfile/goes18?file_name=OR_ABI-L1b-RadC-M6C16_G18_s20222710656169_e20222710658553_c20222710659011.nc
@typercli.command()
def copy_geos_s3_bucket(ctx: typer.Context, file_name: str):
    logged_in = False
    payload = {'username': ctx.obj.username, 'password': ctx.obj.password}
    response = requests.post(f"{BASE_URL}/login", data=payload)
    if response.status_code == 200:
        typer.echo("Logged in successfully as {}".format(ctx.obj.username))
        json_data = json.loads(response.text)
        logged_in = True
        access_token = json_data['access_token']
        typer.echo(f"Access Token is {access_token}")
    elif response.status_code == 401:
        typer.echo("Please Register First !!!")
    elif response.status_code == 405:
        typer.echo(response.json())  
    else:
        typer.echo("Incorrect Username or Password Entered !!!")

    if logged_in:
        try:
            response = requests.post(f"{BASE_URL}/aws-s3-fetchfile/goes18?file_name={file_name}", headers={'Authorization': f'Bearer {access_token}'})
            if response.status_code == 200:
                json_data = json.loads(response.text)
                typer.echo("Found URL of the file available on GOES bucket!")
                typer.echo("URL to file: ", json_data)
            elif response.status_code == 404:
                typer.echo("No such file exists at GOES18 location")
            elif response.status_code == 400:
                typer.echo("Invalid filename format for GOES18")
            else:
                typer.echo(response.status_code)
        except requests.exceptions.HTTPError as httperr:
            if response.status_code == 401:
                typer.echo("Unauthorized: Invalid username or password")
            elif response.status_code == 403:
                typer.echo("Forbidden: You do not have permission to access this resource - Sign Back In!")
            else:
                typer.echo(f"HTTP error occurred: {httperr}")
        except requests.exceptions.RequestException as reqerr:
            typer.echo(f"An error occurred: {reqerr}")

@typercli.command()
def copy_nexrad_s3_bucket(ctx: typer.Context, file_name: str):
    logged_in = False
    payload = {'username': ctx.obj.username, 'password': ctx.obj.password}
    response = requests.post(f"{BASE_URL}/login", data=payload)
    if response.status_code == 200:
        typer.echo("Logged in successfully as {}".format(ctx.obj.username))
        json_data = json.loads(response.text)
        logged_in = True
        access_token = json_data['access_token']
        typer.echo(f"Access Token is {access_token}")
    elif response.status_code == 401:
        typer.echo("Please Register First !!!")
    elif response.status_code == 405:
        typer.echo(response.json())  
    else:
        typer.echo("Incorrect Username or Password Entered !!!")

    if logged_in:
        try:
            response = requests.post(f"{BASE_URL}/aws-s3-fetchfile/nexrad?file_name={file_name}", headers={'Authorization': f'Bearer {access_token}'})
            if response.status_code == 200:
                json_data = json.loads(response.text)
                typer.echo("Found URL of the file available on NexRad bucket!")
                typer.echo("URL to file: ", json_data)
            elif response.status_code == 404:
                typer.echo("No such file exists at NexRad location")
            elif response.status_code == 400:
                typer.echo("Invalid filename format for NexRad")
            else:
                typer.echo(response.status_code)
        except requests.exceptions.HTTPError as httperr:
            if response.status_code == 401:
                typer.echo("Unauthorized: Invalid username or password")
            elif response.status_code == 403:
                typer.echo("Forbidden: You do not have permission to access this resource - Sign Back In!")
            else:
                typer.echo(f"HTTP error occurred: {httperr}")
        except requests.exceptions.RequestException as reqerr:
            typer.echo(f"An error occurred: {reqerr}")

# http://localhost:8000/noaa-database/mapdata
@typercli.command()
def nexrad_map_coordinates(ctx: typer.Context):
    logged_in = False
    payload = {'username': ctx.obj.username, 'password': ctx.obj.password}
    response = requests.post(f"{BASE_URL}/login", data=payload)
    if response.status_code == 200:
        typer.echo("Logged in successfully as {}".format(ctx.obj.username))
        json_data = json.loads(response.text)
        logged_in = True
        access_token = json_data['access_token']
        typer.echo(f"Access Token is {access_token}")
    elif response.status_code == 401:
        typer.echo("Please Register First !!!")
    elif response.status_code == 405:
        typer.echo(response.json())  
    else:
        typer.echo("Incorrect Username or Password Entered !!!")

    if logged_in:
        try:
            response = requests.post(f"{BASE_URL}/noaa-database/mapdata", headers={'Authorization': f'Bearer {access_token}'})
            if response.status_code == 200:
                json_data = json.loads(response.text)
                typer.echo("NexRad Locations Latitudes and Longitudes are given below:\n", json_data)
            else:
                typer.echo(response.status_code)
        except requests.exceptions.HTTPError as httperr:
            if response.status_code == 401:
                typer.echo("Unauthorized: Invalid username or password")
            elif response.status_code == 403:
                typer.echo("Forbidden: You do not have permission to access this resource - Sign Back In!")
            else:
                typer.echo(f"HTTP error occurred: {httperr}")
        except requests.exceptions.RequestException as reqerr:
            typer.echo(f"An error occurred: {reqerr}")

@typercli.callback()
def user_login_details(ctx: typer.Context,
                       username: str = typer.Option(..., envvar='APP_USERNAME', help='Username'),
                       password: str = typer.Option(..., envvar='APP_PASSWORD', help='Password')):
    
    """User Login Details"""
    ctx.obj = User(username, password)

if __name__ == "__main__":
    typercli()