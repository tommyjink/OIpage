# Programming Contest Aggregator

## Overview
The Programming Contest Aggregator is a Python - based project designed to simplify the process of tracking upcoming programming contests. It fetches information from popular platforms such as LeetCode, Codeforces, AtCoder, and Nowcoder, then consolidates it into a single, user - friendly HTML page. The data is updated periodically, ensuring you always have access to the latest contest schedules.

## Features
### 1. Multi - platform Data Retrieval
- **LeetCode**: Uses GraphQL queries to extract details like contest name, start time, and duration.
- **Codeforces**: Calls the official API to get an organized list of upcoming contests sorted by start time.
- **AtCoder**: Parses the homepage HTML with BeautifulSoup to obtain contest names and start times.
- **Nowcoder**: Extracts comprehensive contest data, including start and end times, participant counts, and links, from its contest page HTML.

### 2. Attractive HTML Generation
- Integrates all retrieved contest information into an HTML file.
- Applies CSS styling for an aesthetically pleasing and easy - to - read layout.
- Displays last update time, current time (with real - time updates via JavaScript), and website author details.

### 3. Automated Updates
Executes data collection and HTML file updates at a configurable interval (default is 60 seconds), keeping the information fresh without manual intervention.

## Installation and Setup
1. **Install Dependencies**:
    - Ensure you have Python installed. Then, install the required libraries using `pip install requests beautifulsoup4`.
2. **Save the Script**:
    - Copy the provided Python code and save it as `contest_scraper.py`.
3. **Run the Script**:
    - Navigate to the directory containing the script in your terminal.
    - Execute `python contest_scraper.py`.

## Usage
After running the script, an `index.html` file will be generated in the current directory. Open this file in your web browser to view a consolidated list of upcoming contests from all supported platforms.

## Notes
- **Web Structure Changes**: Platforms may change their web page structures, which could require adjustments to the script. Keep an eye on any errors and update the parsing logic accordingly.
- **Rate Limiting**: Frequent requests may cause your IP to be blocked by the platforms. Set a reasonable update interval to avoid this issue.
- **Debugging**: The script is designed to catch and log exceptions. Use the printed error messages to troubleshoot any issues that may arise.

## Contributing
Contributions to this project are welcome! If you find a bug, have a feature request, or want to improve the code, please open an issue or submit a pull request on GitHub. 
