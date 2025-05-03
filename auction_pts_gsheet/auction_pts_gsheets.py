import os
import requests
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import time

def scrape_points(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'TE': 'Trailers',
        'Referer': 'https://www.espncricinfo.com/',
        'Cookie': 'YOUR_COOKIES_HERE' 
    }
    time.sleep(2)

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 403:
            print("Access Denied: The website is blocking automated requests")
            print("Trying with Selenium instead...")
            return scrape_points_with_selenium(url)
            
        if response.status_code != 200:
            print(f"Failed to fetch data: Status code {response.status_code}")
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')
        points_data = {}
        
        players = soup.find_all('tr')
        players = players[1:]  
        # print(players)
        for player in players:
            try:
                name = player.find('span', {'class': 'ds-text-tight-s ds-font-medium ds-text-typo hover:ds-text-typo-primary ds-block ds-ml-2 ds-text-left ds-cursor-pointer'}).text.strip()
                points = player.find('td', {'class': 'ds-w-0 ds-whitespace-nowrap ds-min-w-max ds-font-bold'}).text.strip()
                points_data[name] = float(points)
            except:
                continue
        # print(points_data)
        return points_data

    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {str(e)}")
        return {}

def scrape_points_with_selenium(url):
    try:
        try:
            print("Trying with undetected_chromedriver...")
            import undetected_chromedriver as uc
            import time
            from selenium.webdriver.common.by import By
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            print("Initializing undetected Chrome driver...")
            driver = uc.Chrome(options=options)
            
            print(f"Navigating to URL: {url}")
            driver.get(url)
            
            print("Waiting for page to load...")
            time.sleep(15)  
            
            print("Extracting player data...")
            points_data = {}
            rows = driver.find_elements(By.TAG_NAME, "tr")
            print(f"Found {len(rows)} rows")
            
            for row in rows[1:]: 
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > 1:
                        
                        try:
                            name_element = row.find_element(By.CSS_SELECTOR, "span[class*='ds-font-medium']")
                            name = name_element.text.strip()
                        except:
                            name = cells[0].text.strip()
                        
                        
                        points = cells[-1].text.strip()
                        
                        
                        if name and points and points.replace('.', '', 1).isdigit():
                            points_data[name] = float(points)
                            print(f"Found player: {name} with {points} points")
                except Exception as e:
                    print(f"Row parsing error: {str(e)}")
                    continue
            
            print(f"Found {len(points_data)} players with undetected_chromedriver")
            driver.quit()
            return points_data
            
        except (ImportError, Exception) as uc_error:
            print(f"undetected_chromedriver error: {uc_error}")
            return {}
            
            
            
            
    except Exception as e:
        print(f"Selenium error: {str(e)}")
        return {}


def update_google_sheet(spreadsheet_id, sheet_name, new_points):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    try:
        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=SCOPES
        )
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return False

    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('No data found in the Google Sheet')
            return False
        header_row = values[0]
        name_col_idx = header_row.index('Name') if 'Name' in header_row else -1
        points_col_idx = header_row.index('Points') if 'Points' in header_row else -1
        
        roles_col_idx = header_row.index('Role') if 'Role' in header_row else -1
        
        if name_col_idx == -1 or points_col_idx == -1 or roles_col_idx == -1:
            print("Required columns 'Name' or 'Points' not found in the sheet")
            return False
            
        
        updates = []
        for i, row in enumerate(values[1:], start=2): 
            if len(row) > name_col_idx:
                player_name = row[name_col_idx]
                if player_name in new_points:
                    print(player_name+"\n")
                    cell_range = f'{sheet_name}!{chr(65 + points_col_idx)}{i}'
                    mul = 1
                    if len(row) > roles_col_idx:
                        if row[roles_col_idx] == 'Captain':
                            mul = 2
                        elif row[roles_col_idx] == 'Vice':
                            mul = 1.5
                    new_points[player_name] = new_points[player_name] * mul
                    
                    updates.append({
                        'range': cell_range,
                        'values': [[new_points[player_name]]]
                    })
        
        if updates:
            body = {
                'valueInputOption': 'USER_ENTERED',
                'data': updates
            }
            result = service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body).execute()
            print(f"{result.get('totalUpdatedCells')} cells updated.")
            return True
        else:
            print("No matching players found to update.")
            return False
            
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        return False

def main():
    url = input("Points list URL: ")
    spreadsheet_id = input("Google Spreadsheet ID: ")
    sheet_name = "Sheet1"
    
    try:
        print("Scraping points data...")
        points_data = scrape_points(url)
        
        if points_data:
            print(f"Found points data for {len(points_data)} players")
            success = update_google_sheet(spreadsheet_id, sheet_name, points_data)
            
            if success:
                print("Points updated successfully!")
            else:
                print("Failed to update points.")
        else:
            print("No points data was retrieved.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
if __name__ == "__main__":
    main()