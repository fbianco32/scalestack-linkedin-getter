import requests
import argparse
import os
import time
import math
from dotenv import load_dotenv
import psutil


BASE_URL = "https://apis.scalestack.io/company"


def get_resource_usage():
    process = psutil.Process(os.getpid())
    cpu_time = process.cpu_times().user + process.cpu_times().system
    memory_info = process.memory_info()
    memory_usage = memory_info.rss 
    return cpu_time, memory_usage

def round_to_significant_figures(value, significant_figures):
    if value == 0:
        return 0
    else:
        return round(value, significant_figures - int(math.floor(math.log10(abs(value)))) - 1)

def argument_parser():
    argumentParser = argparse.ArgumentParser(
        description=""
    )
    company_name = argumentParser.add_argument("--company-name", "-cn", required=True, type=str)
    company_domain = argumentParser.add_argument("--company-domain", "-cd", required=False, type=str)
    return argumentParser.parse_args()

def verify_linkedin_url(name, json_data, domain=None):
    if json_data["name"].lower() != name.lower() or (domain is not None and json_data['domain'].lower() != domain.lower()):
        return "There was an error: Company not found"
    else:
        return json_data['linkedinUrl']


if(__name__ == "__main__"):
    start_time = time.time()
    cpu_start, memory_start = get_resource_usage()
    load_dotenv()
    try:
        args = argument_parser()
        payload = {
            'name': args.company_name,
            'apiKey': os.getenv('API_KEY')
        }
        if(args.company_domain is not None):
            payload['domain'] = args.company_domain
        r = requests.get(BASE_URL, params=payload)
        r.raise_for_status()
        linkedin_url = verify_linkedin_url(args.company_name, r.json(), args.company_domain)

        print(linkedin_url)
    except Exception as e:
        if(hasattr(e, 'response') and e.response.status_code == 404):
            print("There was an error: Company not found")
        else:
            print("There was an error")
    finally:
        cpu_end, memory_end = get_resource_usage()
        end_time = time.time()
        
        duration = end_time - start_time
        cpu_usage = cpu_end - cpu_start
        memory_usage = (memory_end - memory_start) / (1024 ** 2)

        print("Script computational cost:")
        print("Duration: " + str(round_to_significant_figures(duration, 3)) + " seconds")
        print("CPU usage: " + str(round_to_significant_figures(cpu_usage, 3)) + " CPU seconds")
        print("Memory Usage: " + str(round_to_significant_figures(memory_usage, 3)) + "MB")
        
