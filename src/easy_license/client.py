from uuid import getnode
import requests


LICENSE_API_ROOT = "https://fakestoreapi.com"

def register(application, vat_id):
    with requests.Session() as ss:
        api_url = f"{LICENSE_API_ROOT}/auth/login"
        data = dict(username="john_doe", password="pass123")
        response = ss.post(api_url, json=data)
        print(response.text, response.request.__dict__)
        response.raise_for_status()
        response_data = response.json()
        print(response_data)



if __name__ == "__main__":
    import sys
    print("ran with", sys.argv)
    register(sys.argv[0], vat_id="1231231")
