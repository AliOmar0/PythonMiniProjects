import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import quote_plus

class MovieScraper:
    def __init__(self):
        self.base_url = "https://www.imdb.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search_movie(self, query):
        """Search for a movie and return list of results."""
        search_url = f"{self.base_url}/find?q={quote_plus(query)}&s=tt&ttype=ft"
        try:
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            results = []
            # Find movie results
            movie_list = soup.find_all('div', class_='ipc-metadata-list-summary-item__tc')
            
            for movie in movie_list[:5]:  # Limit to first 5 results
                title_elem = movie.find('a', class_='ipc-metadata-list-summary-item__t')
                if title_elem:
                    movie_url = self.base_url + title_elem['href'].split('?')[0]
                    title = title_elem.text.strip()
                    year_elem = movie.find('span', class_='ipc-metadata-list-summary-item__li')
                    year = year_elem.text.strip() if year_elem else "N/A"
                    results.append({
                        'title': title,
                        'year': year,
                        'url': movie_url
                    })
            
            return results
        except requests.RequestException as e:
            print(f"Error searching for movie: {e}")
            return []

    def get_movie_details(self, movie_url):
        """Get detailed information about a specific movie."""
        try:
            # Add delay to respect rate limiting
            time.sleep(1)
            
            response = requests.get(movie_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            details = {}
            
            # Get title
            title_elem = soup.find('span', {'class': 'hero__primary-text'})
            details['title'] = title_elem.text.strip() if title_elem else "N/A"
            
            # Get year
            year_elem = soup.find('a', {'href': re.compile(r'/title/.+/releaseinfo.*')})
            if not year_elem:
                year_elem = soup.find('span', {'class': 'sc-9ab53865-1'})
            details['year'] = year_elem.text.strip() if year_elem else "N/A"
            
            # Get rating
            rating = "N/A"
            # Try first rating location
            rating_elem = soup.find('span', {'class': 'sc-5931bdee-1'})
            if rating_elem:
                # Extract just the rating number using regex
                rating_match = re.search(r'(\d+\.?\d*)', rating_elem.text.strip())
                if rating_match:
                    rating = f"{rating_match.group(1)}/10"
            # Try second rating location
            if rating == "N/A":
                rating_elem = soup.find('span', {'data-testid': 'hero-rating-bar__aggregate-rating__score'})
                if rating_elem:
                    rating_text = rating_elem.text.strip()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = f"{rating_match.group(1)}/10"
            # Try third rating location
            if rating == "N/A":
                rating_div = soup.find('div', {'data-testid': 'hero-rating-bar__aggregate-rating'})
                if rating_div:
                    rating_elem = rating_div.find('span')
                    if rating_elem:
                        rating_text = rating_elem.text.strip()
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            rating = f"{rating_match.group(1)}/10"
            details['rating'] = rating
            
            # Get duration
            duration_elem = soup.find('div', {'data-testid': 'title-techspecs-section'})
            if duration_elem:
                runtime = duration_elem.find('div', class_='ipc-metadata-list-item__content-container')
                details['duration'] = runtime.text.strip() if runtime else "N/A"
            else:
                details['duration'] = "N/A"
            
            # Get genres
            genres = []
            genre_section = soup.find('div', {'data-testid': 'genres'})
            if genre_section:
                genre_links = genre_section.find_all('a')
                genres = [g.text.strip() for g in genre_links if g.text.strip()]
            if not genres:
                genre_section = soup.find('div', {'class': 'ipc-chip-list'})
                if genre_section:
                    genre_spans = genre_section.find_all('span', {'class': 'ipc-chip__text'})
                    genres = [g.text.strip() for g in genre_spans if g.text.strip()]
            details['genres'] = genres
            
            # Get plot summary
            plot_elem = soup.find('span', {'data-testid': 'plot-xl'})
            if not plot_elem:
                plot_elem = soup.find('span', {'data-testid': 'plot-l'})
            details['plot'] = plot_elem.text.strip() if plot_elem else "N/A"
            
            return details
        except requests.RequestException as e:
            print(f"Error getting movie details: {e}")
            return None

def main():
    scraper = MovieScraper()
    
    while True:
        print("\n=== IMDB Movie Information Scraper ===")
        query = input("\nEnter movie title to search (or 'quit' to exit): ")
        
        if query.lower() == 'quit':
            break
        
        print("\nSearching for movies...")
        results = scraper.search_movie(query)
        
        if not results:
            print("No movies found!")
            continue
        
        print("\nFound these movies:")
        for i, movie in enumerate(results, 1):
            print(f"{i}. {movie['title']} ({movie['year']})")
        
        choice = input("\nEnter the number of the movie for more details (or press Enter to search again): ")
        if not choice.strip():
            continue
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(results):
                print("\nFetching movie details...")
                details = scraper.get_movie_details(results[choice-1]['url'])
                
                if details:
                    print("\n=== Movie Details ===")
                    print(f"Title: {details['title']}")
                    print(f"Year: {details['year']}")
                    print(f"Rating: {details['rating']}")
                    print(f"Duration: {details['duration']}")
                    print(f"Genres: {', '.join(details['genres'])}")
                    print(f"\nPlot Summary: {details['plot']}")
                else:
                    print("Could not fetch movie details.")
            else:
                print("Invalid choice!")
        except ValueError:
            print("Invalid input! Please enter a number.")

if __name__ == "__main__":
    main() 