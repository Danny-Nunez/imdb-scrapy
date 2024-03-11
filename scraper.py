import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

def scrape_imdb_movies(imdb_url):
    # Retrieve API key from environment variables
    api_key = os.getenv("SOME_SECRET")
    if api_key is None:
        print("SCRAPINGDOG_API_KEY not found in .env file.")
        return None
    
    url = f"https://api.scrapingdog.com/scrape?api_key={api_key}&url={imdb_url}&render=true"
    
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

def extract_movie_information(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract movie titles, IMDb IDs, and movie images
    movie_titles = [title.text.strip() for title in soup.select('.ipc-metadata-list .ipc-title__text')]
    imdb_ids = [a['href'].split('/')[2] for a in soup.select('.ipc-metadata-list .ipc-title-link-wrapper')]
    movie_images = []
    for img in soup.select('.ipc-metadata-list .ipc-media img'):
        srcset = img['srcset'].split(', ')
        # Select the third URL from the srcset attribute
        image = srcset[2].split()[0]
        movie_images.append(image)
    
    # Store movie information in a list of dictionaries
    movies_info = []
    for title, imdb_id, image in zip(movie_titles, imdb_ids, movie_images):
        movie_info = {
            "Movie Title": title,
            "IMDb ID": imdb_id,
            "Movie Image": image
        }
        movies_info.append(movie_info)
    
    return movies_info

if __name__ == "__main__":
    imdb_url = "https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm"
    
    html_content = scrape_imdb_movies(imdb_url)
    if html_content:
        movies = extract_movie_information(html_content)
        
        # Write movie information to JSON file
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        with open(os.path.join(results_dir, "results.json"), "w") as f:
            json.dump(movies, f, indent=4)
        
        # Print movie information
        for movie in movies:
            print("Movie Title:", movie["Movie Title"])
            print("IMDb ID:", movie["IMDb ID"])
            print("Movie Image:", movie["Movie Image"])
            print()
