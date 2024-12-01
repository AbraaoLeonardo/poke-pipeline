from configparser import ConfigParser
import logging
import requests
import json
from datetime import datetime
import os
from pathlib import Path

def get_api_url(limit: int = 50) -> str:
    """
    Retrieves the API URL from the configuration file and appends the given limit.
    
    Args:
        limit (int): The limit to be appended to the API URL. Default is 50.
        
    Returns:
        str: The full API URL with the limit.
        
    Raises:
        FileNotFoundError: If the configuration file is missing.
        KeyError: If the API section or URL is not found in the configuration.
    """
    config_file = "config/api.conf"
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
    
    config = ConfigParser()
    config.read(config_file)

    try:
        api_url = config.get("api", "api_url")
    except KeyError:
        raise KeyError("Missing 'api_url' in the 'api' section of the config file.")

    return f"{api_url}{limit}"



def get_data(api_url: str = None) -> dict:
    """
    Fetches data from the provided API URL or a default URL.

    Args:
        api_url (str): The API URL to fetch data from. If None, the default URL is used.

    Returns:
        dict: The JSON response data from the API.

    Raises:
        ValueError: If the API URL is not provided and the default URL is unavailable.
        requests.exceptions.HTTPError: If the API request returns an error status code.
    """
    if api_url is None:
        api_url = get_api_url()
    
    response = requests.get(api_url)

    if response.status_code != 200:
        raise requests.exceptions.HTTPError(f"Failed to fetch data. Status code: {response.status_code}")

    return response.json()



def load_data(data: dict) -> None:
    """
    Loads the provided data into a JSON file, storing it in a directory named with today's date.
    
    Args:
        data (dict): The data to be saved, expected to contain a 'results' key.
        
    Raises:
        ValueError: If the 'results' key is missing or the list is empty.
    """
    formated_date = datetime.now().strftime("%Y-%m-%d")
    
    folder_path = Path(os.getcwd()) / "data" / formated_date
    folder_path.mkdir(parents=True, exist_ok=True)

    results = data.get("results")

    if not results:
        raise ValueError("'results' key is missing or empty in the provided data.")

    last_pokemon = data.get("results")[-1]
    last_id = last_pokemon.get("url").split("/")[-2]
    
    file_path = f"{folder_path}/{last_id}.json"

    
    with open(file_path,'w') as file:
        json.dump(results,file)
    return None

def main():
    url = None
    
    while True:
        try:
            data = get_data(url)
            load_data(data)
            next_url = data.get("next")
            if not next_url:
                logging.info("No more pages to fetch. Exiting loop.")
                break

            url = next_url
            logging.info(f"Fetching next page: {url}")

        except Exception as e:
            logging.error(f"Error occurred while processing data: {e}")
            break



def setup_logging():
    """
    Sets up logging to both console and file.
    """
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)
    
    log_file = os.path.join(log_directory, "app.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(log_file)

    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

if __name__ == "__main__":
    setup_logging()

    main()
    logging.info("The project has finished with success")
