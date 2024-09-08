import requests
import csv
from tqdm import tqdm

def search_github_repositories(search_term):
    # Define the GitHub API URL for repository search
    url = "https://api.github.com/search/repositories"
    
    # Initialize parameters for the first page
    params = {
        "q": search_term,
        "per_page": 100,  # Number of results per page (max is 100)
        "sort": "stars",  # Sort by the number of stars
        "order": "desc",  # Order by descending
        "page": 1         # Start with the first page
    }
    
    # Initialize a dictionary to store the repository language logs
    language_log = {}
    total_repos = 0  # Counter for the total number of repositories
    not_specified_repos = []  # List to store "Not Specified" repos
    
    # Initialize tqdm progress bar
    pbar = tqdm(desc="Fetching repositories", unit="repos", leave=False)

    while True:
        # Send a GET request to the GitHub API
        response = requests.get(url, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            repositories = data['items']
            
            # Update total repositories count and progress bar
            repo_count = len(repositories)
            total_repos += repo_count
            pbar.update(repo_count)
            
            # Log the programming language used in each repository
            for repo in repositories:
                language = repo['language'] if repo['language'] else "Not specified"
                normalized_language = language.upper()  # Normalize to uppercase
                
                if language == "Not specified":
                    not_specified_repos.append({
                        'full_name': repo['full_name'],
                        'url': repo['html_url']
                    })
                
                if normalized_language in language_log:
                    language_log[normalized_language] += 1
                else:
                    language_log[normalized_language] = 1
            
            # Check if there are more pages
            if 'next' in response.links:
                params['page'] += 1  # Move to the next page
            else:
                break  # No more pages, exit the loop
        
        else:
            print(f"Failed to retrieve repositories: {response.status_code}")
            break
    
    # Close the progress bar
    pbar.close()
    
    # Save "Not Specified" repos to CSV
    save_not_specified_repos(not_specified_repos)
    
    return language_log, total_repos

def save_not_specified_repos(not_specified_repos):
    # Define the CSV file path
    csv_file = 'not_specified_repos.csv'
    
    # Define the CSV headers
    headers = ['full_name', 'url']
    
    # Write to the CSV file
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(not_specified_repos)
    
    print(f"\nSaved {len(not_specified_repos)} 'Not Specified' repositories to '{csv_file}'.")

def print_language_distribution(language_log, total_repos):
    other_count = 0  # Counter for languages with <2% usage
    significant_languages = {}
    other_languages = {}  # Keep track of languages in "Other"
    
    # Calculate percentage and categorize languages
    for language, count in language_log.items():
        percentage = (count / total_repos) * 100
        if percentage < 2 and language != "NOT SPECIFIED":
            other_count += count
            other_languages[language] = (percentage, count)
        else:
            significant_languages[language] = (percentage, count)
    
    # Print significant languages
    print("Language distribution:")
    for language, (percentage, count) in significant_languages.items():
        print(f"{language}: {percentage:.2f}% ({count} repositories)")
    
    # Always print 'Not Specified' if it exists
    if "NOT SPECIFIED" in language_log:
        not_specified_count = language_log["NOT SPECIFIED"]
        not_specified_percentage = (not_specified_count / total_repos) * 100
        print(f"NOT SPECIFIED: {not_specified_percentage:.2f}% ({not_specified_count} repositories)")
    
    # Print 'Other' category and its components if there are languages with <2% usage
    if other_count > 0:
        other_percentage = (other_count / total_repos) * 100
        print(f"Other: {other_percentage:.2f}% ({other_count} repositories)")
        print("Composed of:")
        for language, (percentage, count) in other_languages.items():
            print(f"  - {language}: {percentage:.2f}% ({count} repositories)")

# Example usage:
search_term = input("Enter the search term: ")
language_log, total_repos = search_github_repositories(search_term)

if language_log:
    print(f"\nTotal repositories found: {total_repos}")
    print_language_distribution(language_log, total_repos)
