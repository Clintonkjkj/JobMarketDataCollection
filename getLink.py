import requests

def get_searchLink(job,location):
    base_url = 'https://api.glassdoor.com/api/api.htm?t.p=5317&t.k=APIKEY&userip=0.0.0.0&format=json&v=1&action=jobs&l='+location+'&q='+job
    print(base_url)
    headers = {'user-agent': 'Mozilla/5.0',}
    response = requests.get(base_url,headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['response']['attributionURL']
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None

