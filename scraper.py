import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

def scrape_indeed_jobs(job_search_url):
    # Retrieve API key from environment variables
    api_key = os.getenv("SOME_SECRET")
    if api_key is None:
        print("API_KEY not found in .env file.")
        return None
    
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

def extract_job_information(html_content):
    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract job titles and URLs
    job_titles = [title.text.strip() for title in soup.find_all('h2', class_='jobTitle')]
    job_urls = [f"https://indeed.com{title.a['href']}" for title in soup.find_all('h2', class_='jobTitle')]
    
    # Extract company names and locations within the class css-1p0sjhy
    company_names = []
    company_locations = []
    for location in soup.find_all(class_='company_location'):
        css_1p0sjhy_div = location.find('div', class_='css-1p0sjhy eu4oa1w0')
        if css_1p0sjhy_div:
            company_locations.append(css_1p0sjhy_div.text.strip())
            company_name_span = location.find('span', class_='css-92r8pb eu4oa1w0')
            if company_name_span:
                company_names.append(company_name_span.text.strip())
            else:
                company_names.append("N/A")  # Placeholder if company name is not found
    
    job_metadata = [metadata.text.strip() for metadata in soup.find_all(class_='jobMetaDataGroup')]
    job_metadata = [metadata.replace('provided', 'provided ') if 'provided' in metadata else metadata for metadata in job_metadata]  
    job_metadata = [metadata.replace('year', 'year ') if 'year' in metadata else metadata for metadata in job_metadata]
    job_metadata = [metadata.replace('month', 'month ') if 'month' in metadata else metadata for metadata in job_metadata] 
    job_metadata = [metadata.replace('hour', 'hour ') if 'hour' in metadata else metadata for metadata in job_metadata]    
    
    # Clean job descriptions
    job_descriptions = []
    for description in soup.find_all(class_='underShelfFooter'):
        cleaned_description = description.text.strip().split('PostedPosted')[0]
        cleaned_description = cleaned_description.replace('\u2026', '').replace('\u2019', '').replace('\n', '')
        job_descriptions.append(cleaned_description)
    
    return job_titles, job_urls, company_names, company_locations, job_metadata, job_descriptions





if __name__ == "__main__":
    job_search_url = "https://www.indeed.com/q-citibank-jobs.html?vjk=234418ba30a2eecd"
    
    html_content = scrape_indeed_jobs(job_search_url)
    if html_content:
        job_titles, job_urls, company_names, company_locations, job_metadata, job_descriptions = extract_job_information(html_content)
        
        # Store job information in a list of dictionaries
        jobs = []
        for title, url, name, location, metadata, description in zip(job_titles, job_urls, company_names, company_locations, job_metadata, job_descriptions):
            job_info = {
                "Job Title": title,
                "Job URL": url,
                "Company Name": name,
                "Company Location": location,
                "Salary": metadata,
                "Job Description": description
            }
            jobs.append(job_info)
        
        # Write job information to JSON file
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        with open(os.path.join(results_dir, "results.json"), "w") as f:
            json.dump(jobs, f, indent=4)
        
        # Print job information
        for job in jobs:
            print("Job Title:", job["Job Title"])
            print("Job URL:", job["Job URL"])
            print("Company Name:", job["Company Name"])
            print("Company Location:", job["Company Location"])
            print("Salary:", job["Salary"])
            print("Job Description:", job["Job Description"])
            print()
