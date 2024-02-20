import os
import requests
import json
from bs4 import BeautifulSoup

def scrape_indeed_jobs(job_search_url):
    api_key = os.environ.get("SOME_SECRET")
    url = f"https://api.scrapingdog.com/scrape?api_key={api_key}&url={job_search_url}&dynamic=false"
    
    # Make the HTTP GET request
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Return the parsed HTML content
        return response.content
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def extract_job_information(html_content, job_search_url):
    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract job title and URL
    job_titles = []
    job_ids = []  # New list to store job IDs
    for job_title in soup.find_all('h2', class_='jobTitle'):
        job_titles.append(job_title.text.strip())
        job_id = job_title.a['data-jk']  # Extract job ID
        job_ids.append(job_id)
        
    # Generate job URLs using job IDs
    job_urls = [f"{job_search_url}&jk={job_id}" for job_id in job_ids]
        
    # Extract company location
    company_locations = [location.text.strip() for location in soup.find_all(class_='company_location')]
    
    # Extract job descriptions
    job_descriptions = [description.text.strip() for description in soup.find_all(class_='jcsSpacingFontUpdate')]
    
    # Extract job metadata (including salary information)
    job_metadata = []
    for metadata in soup.find_all(class_='jobMetaDataGroup'):
        metadata_text = metadata.text.strip()
        # Check if metadata contains salary information
        salary = metadata.find(class_='salary-snippet')
        if salary:
            metadata_text += f"\nSalary: {salary.text.strip()}"
        job_metadata.append(metadata_text)
    
    return job_titles, job_urls, company_locations, job_metadata, job_descriptions

def organize_data_by_title(job_titles, job_urls, company_locations, job_metadata, job_descriptions):
    # Initialize dictionary to store job information by title
    job_info_by_title = {}
    
    # Iterate over the data and organize it by job title
    for title, url, location, metadata, description in zip(job_titles, job_urls, company_locations, job_metadata, job_descriptions):
        # Create dictionary for the current job
        job_info = {
            'Job Title': title,
            'Job URL': url,
            'Location': location,
            'Metadata': metadata,
            'Description': description
        }
        
        # Add job information to the dictionary, organized by title
        if title not in job_info_by_title:
            job_info_by_title[title] = []
        job_info_by_title[title].append(job_info)
    
    return job_info_by_title

if __name__ == "__main__":
    job_search_url = "https://www.indeed.com/cmp/Meta-dd1502f2/jobs?q=&l=Arlington%2C+VA"
    
    html_content = scrape_indeed_jobs(job_search_url)
    if html_content:
        job_titles, job_urls, company_locations, job_metadata, job_descriptions = extract_job_information(html_content, job_search_url)
        
        # Organize data by job title
        job_info_by_title = organize_data_by_title(job_titles, job_urls, company_locations, job_metadata, job_descriptions)
        
        # Check if there are no job results
        if not job_info_by_title:
            no_jobs_message = {"Message": "Currently no jobs available"}
            results_folder = 'results'
            results_file = os.path.join(results_folder, 'results.json')
            os.makedirs(results_folder, exist_ok=True)
            with open(results_file, 'w') as f:
                json.dump(no_jobs_message, f, indent=4)
        else:
            # Save job information to JSON file
            results_folder = 'results'
            results_file = os.path.join(results_folder, 'results.json')
            os.makedirs(results_folder, exist_ok=True)
            with open(results_file, 'w') as f:
                json.dump(job_info_by_title, f, indent=4)