import json
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_from_file(file_path):
    """
    Loads data from a JSON file. If the file doesn't exist, creates an empty file and returns an empty dictionary.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Data loaded from the file, or an empty dictionary if the file doesn't exist or cannot be loaded.
    """
    try:
        if not os.path.exists(file_path):
            logging.warning(f"File {file_path} not found. Creating an empty index file.")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)  # Create an empty JSON object
            return {}

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Error loading file {file_path}: {e}")
        return {} #Return an empty dict.
    except FileNotFoundError as e:
        logging.error(f"Error loading file {file_path}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Error loading file {file_path}: {e}")
        return {}


def save_to_file(file_path, data):
    """
    Saves data to a JSON file.

    Args:
        file_path (str): Path to the JSON file.
        data (dict): Data to save.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def validate_index_file(file_path):
    """
    Validate the index file. If the file doesn't exist, create a new one.
    
    Args:
        file_path (str): Path to the index file
    """
    try:
        if not os.path.exists(file_path):
            logging.warning(f"Index file {file_path} not found. Creating a new one.")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)  # Create an empty JSON object
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
    except FileNotFoundError as e:
        logging.error(f"Error validating index file {file_path}: {e}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error validating index file {file_path}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Error validating index file {file_path}: {e}")
        return {}

def get_repository_config(config_path):
    """
    Loads the repository URL and clone directory from the config file.

    Args:
        config_path (str): Path to the config file.

    Returns:
        tuple: Repository URL and clone directory, or (None, None) if not found.
    """
    try:
        if not os.path.exists(config_path):
            logging.error(f"Config file {config_path} not found.")
            return None, None
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("repo_url"), config.get("clone_dir")
    except Exception as e:
        logging.error(f"Error reading config file {config_path}: {e}")
        return None, None