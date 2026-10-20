
import requests
import json
import time

def has_data_for_date(date):
    test_asn = 1
    url = f"https://api.rovista.netsecurelab.org/rovista/api/inference-results/{test_asn}?date={date[0:4]}-{date[4:6]}-{date[6:8]}"
    
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def get_rovista_invalid(date):
   
    rovista_results = f"../dataset/rovista/rovista_prefix_{date}.json"

    invalid_prefix_data = {}

    count = 0

    asn = "1"
    key = f"{asn}"
 
    print(f"[{count}] Requesting AS{key}", flush=True)

    url = f"https://api.rovista.netsecurelab.org/rovista/api/inference-results/{asn}?date={date[0:4]}-{date[4:6]}-{date[6:8]}"

    try:
        response = requests.get(
            url,
            #headers=headers,
            timeout=10
        )

        print(f"[{count}] Status {response.status_code} for AS{key}", flush=True)

        if response.status_code == 200:
            data = response.json()
            invalid_prefix_data = data

    except Exception as e:
        print(f"Error AS{key}: {e}", flush=True)

    # avoid hammering API
    time.sleep(0.01)

    with open(rovista_results, "w") as f:
        json.dump(invalid_prefix_data, f)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 ./run.sh")
    else:
        date = sys.argv[1]

        if not has_data_for_date(date):
            print(f"No data for {date}, skipping...", flush=True)
            exit(0)

        get_rovista_invalid(date)