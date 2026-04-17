import requests
import os
from pathlib import Path

project_root = Path(__file__).parent.parent

# Configuration dictionary
configurations = {
    "8.5": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.5/apache/Dockerfile",
        "end_phrase": "find /etc/apache2 -type f -name '*.conf' -exec sed -ri 's/([[:space:]]*LogFormat[[:space:]]+\"[^\"]*)%h([^\"]*\")/\\1%a\\2/g' '{}' +",
        "dockerfile_path": project_root / "php8.5/Dockerfile"
    },
    "8.5-fpm": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.5/fpm/Dockerfile",
        "end_phrase": '} > "$PHP_INI_DIR/conf.d/error-logging.ini"',
        "dockerfile_path": project_root / "php8.5-fpm/Dockerfile"
    },
    "8.4": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.4/apache/Dockerfile",
        "end_phrase": "find /etc/apache2 -type f -name '*.conf' -exec sed -ri 's/([[:space:]]*LogFormat[[:space:]]+\"[^\"]*)%h([^\"]*\")/\\1%a\\2/g' '{}' +",
        "dockerfile_path": project_root / "php8.4/Dockerfile"
    },
    "8.4-fpm": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.4/fpm/Dockerfile",
        "end_phrase": '} > "$PHP_INI_DIR/conf.d/error-logging.ini"',
        "dockerfile_path": project_root / "php8.4-fpm/Dockerfile"
    },
    "8.3": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.3/apache/Dockerfile",
        "end_phrase": "find /etc/apache2 -type f -name '*.conf' -exec sed -ri 's/([[:space:]]*LogFormat[[:space:]]+\"[^\"]*)%h([^\"]*\")/\\1%a\\2/g' '{}' +",
        "dockerfile_path": project_root / "php8.3/Dockerfile"
    },
    "8.3-fpm": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.3/fpm/Dockerfile",
        "end_phrase": '} > "$PHP_INI_DIR/conf.d/error-logging.ini"',
        "dockerfile_path": project_root / "php8.3-fpm/Dockerfile"
    },
    "8.2": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.2/apache/Dockerfile",
        "end_phrase": "find /etc/apache2 -type f -name '*.conf' -exec sed -ri 's/([[:space:]]*LogFormat[[:space:]]+\"[^\"]*)%h([^\"]*\")/\\1%a\\2/g' '{}' +",
        "dockerfile_path": project_root / "php8.2/Dockerfile"
    },
    "8.2-fpm": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.2/fpm/Dockerfile",
        "end_phrase": '} > "$PHP_INI_DIR/conf.d/error-logging.ini"',
        "dockerfile_path": project_root / "php8.2-fpm/Dockerfile"
    }
}

# Process Dockerfile for each version
for version, config in configurations.items():
    print(f"Processing version {version}.")

    # Download and get text content
    response = requests.get(config["download_url"])
    lines = response.text.split('\n')

    # Identify the range to extract
    start_phrase = "# persistent dependencies"
    end_phrase = config["end_phrase"]
    start_index = end_index = None

    for i, line in enumerate(lines):
        if start_phrase in line:
            start_index = i
        elif end_phrase in line and start_index is not None:
            end_index = i
            break

    # Save the extracted section to .temp.txt
    temp_file = Path(__file__).parent / ".temp.txt"
    if start_index is not None and end_index is not None:
        with open(temp_file, 'w') as file:
            for line in lines[start_index:end_index + 1]:
                file.write(line + '\n')

        print(f"Extraction complete, saved to {temp_file}.")

        # Dockerfile path
        dockerfile_path = config["dockerfile_path"]

        # Start and end markers for the replacement range
        start_marker = "# The official WordPress Dockerfile START\n"
        end_marker = "# The official WordPress Dockerfile END\n"

        # Read the Dockerfile
        with open(dockerfile_path, 'r') as file:
            dockerfile_contents = file.readlines()

        # Find the replacement range
        start_index = end_index = None
        for i, line in enumerate(dockerfile_contents):
            if line.strip() == start_marker.strip():
                start_index = i
            elif line.strip() == end_marker.strip() and start_index is not None:
                end_index = i
                break

        # Replace the range
        if start_index is not None and end_index is not None:
            with open(temp_file, 'r') as file:
                replacement_content = file.readlines()

            dockerfile_contents[start_index:end_index + 1] = [start_marker] + replacement_content + [end_marker]

            # Save the changes
            with open(dockerfile_path, 'w') as file:
                file.writelines(dockerfile_contents)

            print(f"Dockerfile ({dockerfile_path}) replacement complete.")
        else:
            print("Specified range not found in Dockerfile.")

        # Remove .temp.txt
        os.remove(temp_file)
        print(f"{temp_file} removed.")
    else:
        print("Specified range not found in the source file.")
