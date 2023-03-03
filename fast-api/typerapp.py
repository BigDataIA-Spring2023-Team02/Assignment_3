import typer
import requests
import json
from enum import Enum 
from wsgiref import headers

class Plan(str, Enum):
    free = 'Free'
    gold = 'Gold'
    platinum = 'Platinum'

BASE_URL = "http://localhost:8001"

app = typer.Typer()
users_app = typer.Typer()
app.add_typer(users_app, name="users")
session = requests.session()
headers = session.headers

@users_app.command("create-new-user")
def create_new_user(full_name: str = typer.Option('', prompt = "Enter your full name"),
                username: str = typer.Option('', prompt = "Enter your username"),
                password : str = typer.Option('', prompt = "Please enter your password", confirmation_prompt= True),
                plan : Plan = typer.Option('', prompt = "Please choose a plan"),
                user_type : str = typer.Option(["User, Admin"], prompt = "Are you a user or admin?")):
    payload = {'full_name': full_name, 'username': username, 'password': password, 'plan': plan, 'user_type' : user_type}
    response = requests.post(f"{BASE_URL}/user/create", json = payload)
    typer.echo(f"Creating user: {username} in plan: {plan}")   

@users_app.command("login-user")
def user_login(username : str = typer.Option('', prompt = "Enter Username"),
          password: str = typer.Option('', prompt = "Enter Password")):
    global headers
    payload = {'username' : username, 'password' : password}
    response = requests.post(f"{BASE_URL}/login", data = payload)
    json_data = json.loads(response.text)
    if response.status_code == 200:
        access_token = json_data['access_token']
        headers['Authorization'] = f"Bearer {access_token}"
        session.headers.update({'Authorization': 'Bearer ' + access_token})  
        typer.echo(session.headers)
    else:
        typer.echo("Incorrect username or password.")

@users_app.command("change-user-password")
def change_user_password(username: str = typer.Option('', prompt = "Enter username"),
                    new_password: str = typer.Option('', prompt = "Enter new password", confirmation_prompt=True)):
    payload = {'password' : new_password}
    response = requests.patch(f"{BASE_URL}/user/update?username={username}", json=payload, headers = headers)
    if response.status_code == 200:
        typer.echo("Password updated successfully!")
    else:
        typer.echo(response)

@users_app.command("generate-url-filename")
def generate_url_by_filename(username : str = typer.Option('', prompt = "Enter Username to login"),
                         password : str = typer.Option('', prompt = "Enter Password"),
                         datasource : str = typer.Option('', prompt = "Choose one - GOES18 or NEXRAD")):
    
    payload = {'username' : username, 'password' : password}
    login_resp = requests.post(f"{BASE_URL}/login", data = payload)
    if login_resp.status_code == 200:
        json_data = json.loads(login_resp.text)
        access_token = json_data['access_token']
        global headers
        headers['Authorization'] = f"Bearer {access_token}"
        
        if datasource == "GOES18":
            file_name = input("Enter file name: ")
            response = requests.post(f"{BASE_URL}/aws-s3-fetchfile/goes18?file_name={file_name}", headers = headers)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                final_url = json_data
                typer.echo("Found URL of the file available on GOES18 bucket!")
                typer.echo("URL to file: ", final_url)
                return
            else:
                typer.echo("Incorrect file name given, please change!")
                return
        
        elif datasource == "NEXRAD":
            file_name = input("Enter file name: ")
            response = requests.post(f"{BASE_URL}/aws-s3-fetchfile/nexrad?file_name={file_name}", headers = headers)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                final_url = json_data
                typer.echo("Found URL of the file available on NEXRAD bucket!")
                typer.echo("URL to file: ", final_url)
                return
            else:
                typer.echo("Incorrect file name given, please change!")
                return
        
        else:
            typer.echo("Please enter one of the 2 options above")
            return
    else:
        typer.echo("Incorrect username or password.")
        return

@users_app.command("fetch-aws-s3-files")
def aws_s3_files_list(username : str = typer.Option('', prompt = "Enter Username to login"),
               password: str = typer.Option('', prompt = "Enter Password"),
               datasource : str = typer.Option('', prompt = "Choose one - GOES18 or NEXRAD")):
    
    payload = {'username' : username, 'password' : password}
    login_resp = requests.post(f"{BASE_URL}/login", data = payload)
    if login_resp.status_code == 200:
        json_data = json.loads(login_resp.text)
        access_token = json_data['access_token']
        global headers
        headers['Authorization'] = f"Bearer {access_token}"
        
        if datasource == "GOES18":
            year = input("Enter year: ")
            day = input("Enter day: ")
            hour = input("Enter hour: ")
            typer.echo("Product is ABI-L1b-RadC by default")
            product = "ABI-L1b-RadC"
            response = requests.get(f"{BASE_URL}/aws-s3-files/goes18?year={year}&day={day}&hour={hour}&product={product}", headers = headers)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                files_in_selected_hour = json_data
                typer.echo("List of files loading...")
                typer.echo(files_in_selected_hour)
                return
            else:
                typer.echo("Incorrect input given, please change the inputs!")
                return
        
        elif datasource == "NEXRAD":
            year = input("Enter year: ")
            month = input("Enter month: ")
            day = input("Enter day: ")
            ground_station = input("Enter ground station: ")
            response = requests.get(f"{BASE_URL}/aws-s3-files/nexrad?year={year}&month={month}&day={day}&ground_station={ground_station}", headers = headers)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                files_in_selected_hour = json_data
                typer.echo("List of files loading...")
                typer.echo(files_in_selected_hour)
                return
            else:
                typer.echo("Incorrect input given, please change the inputs!")
                return
        
        else:
            typer.echo("Please enter one of the 2 options above")
            return
    else:
        typer.echo("Incorrect username or password.")
        return

if __name__ == "__main__":
    app()