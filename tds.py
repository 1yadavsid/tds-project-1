import requests
import csv

# GitHub API token (replace with your actual token)
GITHUB_TOKEN = "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"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Step 1: Fetch users in Dublin with over 50 followers
def get_users_in_dublin():
    users = []
    query = "location:Dublin+followers:>50"
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/search/users?q={query}&per_page={per_page}&page={page}"
        response = requests.get(url, headers=HEADERS)
        print(f"Fetching page {page}...")

        if response.status_code != 200:
            print("Error fetching data:", response.json())
            break

        data = response.json()
        users.extend(data['items'])

        if len(data['items']) < per_page:
            break

        page += 1

    detailed_users = []
    for user in users:
        user_info = get_user_details(user['login'])
        detailed_users.append(user_info)

    return detailed_users

# Step 2: Get detailed information for each user
def get_user_details(username):
    user_url = f"https://api.github.com/users/{username}"
    user_data = requests.get(user_url, headers=HEADERS).json()

    return {
        'login': user_data['login'],
        'name': user_data.get('name', ''),
        'company': clean_company_name(user_data.get('company', '')),
        'location': user_data.get('location', ''),
        'email': user_data.get('email', ''),
        'hireable': user_data.get('hireable', ''),
        'bio': user_data.get('bio', ''),
        'public_repos': user_data['public_repos'],
        'followers': user_data['followers'],
        'following': user_data['following'],
        'created_at': user_data['created_at'],
    }

# Helper function to clean up company names
def clean_company_name(company):
    if company:
        company = company.strip().upper()
        if company.startswith('@'):
            company = company[1:]
    return company

# Step 3: Fetch repositories for each user
def get_user_repos(username):
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=500"
    response = requests.get(repos_url, headers=HEADERS)
    repos_data = response.json()

    repos = []
    for repo in repos_data:
        repos.append({
            'login': username,
            'full_name': repo['full_name'],
            'created_at': repo['created_at'],
            'stargazers_count': repo['stargazers_count'],
            'watchers_count': repo['watchers_count'],
            'language': repo['language'],
            'has_projects': repo['has_projects'],
            'has_wiki': repo['has_wiki'],
            'license_name': repo['license']['key'] if repo['license'] else '',
        })

    return repos

# Step 4: Save user data to users.csv
def save_users_to_csv(users):
    with open('users.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['login', 'name', 'company', 'location', 'email', 'hireable', 'bio', 'public_repos', 'followers', 'following', 'created_at'])
        writer.writeheader()
        writer.writerows(users)

# Step 5: Save repository data to repositories.csv
def save_repos_to_csv(repos):
    with open('repositories.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['login', 'full_name', 'created_at', 'stargazers_count', 'watchers_count', 'language', 'has_projects', 'has_wiki', 'license_name'])
        writer.writeheader()
        writer.writerows(repos)

# Main function to fetch and save data
if __name__ == "__main__":
    # Fetch users in Dublin with >50 followers
    users = get_users_in_dublin()
    save_users_to_csv(users)

    # Fetch repositories for each user
    all_repos = []
    for user in users:
        repos = get_user_repos(user['login'])
        all_repos.extend(repos)

    # Save all repository data
    save_repos_to_csv(all_repos)
    print("Done")
