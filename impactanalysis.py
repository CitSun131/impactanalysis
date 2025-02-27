import os
import logging
import concurrent.futures
from tqdm import tqdm
import shutil
import stat
import git

# Import from the new config_utils module
from utils.config_utils import load_from_file, save_to_file, validate_index_file, get_repository_config
# Import from the new parse_java module
from utils.parse_java import parse_java_file
# Import from the new diagrams module
from diagrams.generate_diagrams import generate_sequence_diagram, generate_c4_diagram, generate_context_diagram, generate_container_diagram, generate_component_diagram
from diagrams.generate_class_diagram import generate_class_diagram

# Setup structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

INDEX_DIR = "code_index"
INDEX_JSON = os.path.join(INDEX_DIR, "index.json")
CONFIG_PATH = os.path.join("config", "config.json")

def scan_directory_incremental(directory):
    """
    Scans the specified directory for Java files and parses them.
    
    Args:
        directory (str): Path to the directory to scan.
    """
    if not os.path.exists(directory):
        logging.error(f"Directory {directory} does not exist. Ensure the repository was cloned successfully.")
        return

    # Load index data only once before starting the parsing
    index_data = load_from_file(INDEX_JSON)

    java_files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith(".java")]
    if not java_files:
        logging.warning(f"No Java files found in {directory}. Skipping indexing.")
        return

    logging.info(f"Found {len(java_files)} Java files in {directory}.")
    errors = []
    with tqdm(total=len(java_files), desc="Indexing Files") as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(parse_java_file, f, directory, index_data): f for f in java_files}
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    errors.append((futures[future], str(e)))
                pbar.update(1)
    
    if errors:
        logging.error(f"Errors occurred in {len(errors)} files:")
        for file, error in errors:
            logging.error(f"{file}: {error}")

    # Save the data after parsing the files.
    save_to_file(INDEX_JSON, index_data)

def clone_repository():
    """
    Clones the repository specified in config.json, or skips if it already exists.
    
    Returns:
        bool: True if successful (cloned or already exists), False otherwise.
    """
    repo_url, clone_dir = get_repository_config(CONFIG_PATH)
    
    if not repo_url:
        logging.error("No repository URL found in config.json. Aborting clone.")
        return False
    
    # Delete the directory in every execution.
    if os.path.exists(clone_dir):
        logging.warning(f"Repository directory {clone_dir} already exists. Deleting it...")
        delete_cloned_repo(clone_dir)
    
    try:
        logging.info(f"Cloning repository {repo_url} into {clone_dir}...")
        git.Repo.clone_from(repo_url, clone_dir)
        logging.info("Repository cloned successfully!")
        return True
    except Exception as e:
        logging.error(f"Error cloning repository: {e}")
        return False

def handle_remove_readonly(func, path, exc_info):
    """
    Handle read-only file deletion on Windows.
    
    Args:
        func (function): The function to call to remove the file
        path (str): The path to the file to remove
        exc_info (tuple): Exception information
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_cloned_repo(directory):
    """
    Delete the cloned repository directory and its contents.
    
    Args:
        directory (str): Path to the directory to delete
    """
    if os.path.exists(directory):
        try:
            shutil.rmtree(directory, onerror=handle_remove_readonly)
            logging.info(f"Deleted directory: {directory}")
        except Exception as e:
            logging.error(f"Error deleting directory {directory}: {e}")
    else:
        logging.warning(f"Directory {directory} does not exist. Skipping deletion.")

def clear_index_directory(directory):
    """
    Clear the contents of the index directory if it exists.
    
    Args:
        directory (str): Path to the directory to clear
    """
    if os.path.exists(directory):
        try:
            shutil.rmtree(directory, onerror=handle_remove_readonly)
            logging.info(f"Cleared directory: {directory}")
        except Exception as e:
            logging.error(f"Error clearing directory {directory}: {e}")
    os.makedirs(directory, exist_ok=True)

def main():
    clear_index_directory(INDEX_DIR)
    if clone_repository():
        scan_directory_incremental("./cloned_repo")
        generate_context_diagram()
        generate_component_diagram()
        generate_class_diagram(INDEX_DIR, INDEX_JSON)
        generate_sequence_diagram()
        delete_cloned_repo("./cloned_repo")

if __name__ == "__main__":
    main()
