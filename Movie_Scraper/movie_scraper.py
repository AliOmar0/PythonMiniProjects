import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def search_movie(query):
    """Search for movies on IMDB"""
    # Format query for URL
    formatted_query = query.replace(" ", "+")
    search_url = f"https://www.imdb.com/find/?q={formatted_query}&s=tt&ttype=ft&ref_=fn_ft"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # Find all search result items
        for item in soup.select('li.ipc-metadata-list-summary-item'):
            # Extract title and year
            title_elem = item.select_one('a.ipc-metadata-list-summary-item__t')
            if title_elem:
                title = title_elem.text.strip()
                link = title_elem['href']
                movie_id = link.split('/')[2]
                
                # Extract year if available
                year_elem = item.select_one('.ipc-metadata-list-summary-item__li')
                year = year_elem.text.strip() if year_elem else "N/A"
                
                results.append({
                    'id': movie_id,
                    'title': title,
                    'year': year
                })
        
        return results
    except Exception as e:
        st.error(f"Error searching for movies: {str(e)}")
        return []

def get_movie_details(movie_id):
    """Get detailed information about a movie"""
    url = f"https://www.imdb.com/title/{movie_id}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {}
        
        # Get title
        title_elem = soup.select_one('h1[data-testid="hero__pageTitle"]')
        details['title'] = title_elem.text.strip() if title_elem else "N/A"
        
        # Get rating
        rating_elem = soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating"]')
        if rating_elem:
            # Get just the rating number (first span)
            rating_text = rating_elem.text.strip()
            # Extract just the first number (rating)
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                rating = rating_match.group(1)
                details['rating'] = f"{rating}/10"
            else:
                details['rating'] = "N/A"
        else:
            details['rating'] = "N/A"
        
        # Get year
        year_elem = soup.select_one('a[href*="releaseinfo"]')
        details['year'] = year_elem.text.strip() if year_elem else "N/A"
        
        # Get duration
        duration = None
        # Look for runtime in the metadata
        metadata_section = soup.find('section', {'cel_widget_id': 'StaticFeature_Details'})
        if metadata_section:
            runtime_div = metadata_section.find(lambda tag: tag.name == 'div' and 'Runtime' in tag.text)
            if runtime_div:
                duration_text = runtime_div.find_next('div').text.strip()
                if duration_text:
                    duration = duration_text

        # Backup method for duration
        if not duration:
            for ul in soup.select('ul.ipc-inline-list'):
                for li in ul.find_all('li'):
                    text = li.text.strip()
                    if 'h' in text or 'm' in text:
                        duration = text
                        break
                if duration:
                    break
        
        details['duration'] = duration if duration else "N/A"
        
        # Get director
        director = None
        # Look for director in the metadata
        for div in soup.find_all('div', class_='ipc-metadata-list-item'):
            label = div.find('span', class_='ipc-metadata-list-item__label')
            if label and 'Director' in label.text:
                link = div.find('a')
                if link:
                    director = link.text.strip()
                    break
        
        # Backup method for director
        if not director:
            for a in soup.find_all('a'):
                if a.parent and 'Director' in a.parent.text and not a.text.startswith('Director'):
                    director = a.text.strip()
                    break
        
        details['director'] = director if director else "N/A"
        
        # Get plot
        plot_elem = soup.select_one('span[data-testid="plot-xl"]')
        if not plot_elem:
            plot_elem = soup.select_one('span[data-testid="plot-l"]')
        if not plot_elem:
            plot_elem = soup.select_one('p[data-testid="plot"]')
        details['plot'] = plot_elem.text.strip() if plot_elem else "N/A"
        
        # Debug output
        st.write("Debug - HTML Structure:")
        st.write("Rating text:", rating_text if 'rating_text' in locals() else "None")
        
        # Show relevant HTML sections for debugging
        st.write("Metadata section found:", bool(metadata_section))
        if metadata_section:
            st.write("Runtime div found:", bool(runtime_div) if 'runtime_div' in locals() else False)
        
        # Show all text containing "Director" for debugging
        director_elements = []
        for elem in soup.find_all(string=lambda text: text and 'Director' in text):
            director_elements.append(elem.strip())
        st.write("Elements containing 'Director':", director_elements)
        
        return details
    except Exception as e:
        st.error(f"Error getting movie details: {str(e)}")
        return {
            'title': "Error",
            'rating': "N/A",
            'year': "N/A",
            'duration': "N/A",
            'director': "N/A",
            'plot': "Could not fetch movie details"
        }

def main():
    st.title("Movie Information Scraper")
    st.write("Search for movies and get detailed information from IMDB")
    
    # Search box
    search_query = st.text_input("Enter movie title to search:")
    
    if search_query:
        with st.spinner("Searching..."):
            results = search_movie(search_query)
            # Add a small delay to prevent too many rapid requests
            time.sleep(0.5)
        
        if results:
            st.subheader("Search Results")
            
            # Display results in a more user-friendly way
            for idx, movie in enumerate(results):
                with st.container():
                    # Initialize session state for this movie if not exists
                    if f'show_details_{idx}' not in st.session_state:
                        st.session_state[f'show_details_{idx}'] = False
                    
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.write(f"**{movie['title']}** ({movie['year']})")
                    
                    with col2:
                        if not st.session_state[f'show_details_{idx}']:
                            if st.button("View Details", key=f"view_{idx}"):
                                st.session_state[f'show_details_{idx}'] = True
                                st.rerun()
                        else:
                            if st.button("Hide Details", key=f"hide_{idx}"):
                                st.session_state[f'show_details_{idx}'] = False
                                st.rerun()
                    
                    # Show details if requested
                    if st.session_state[f'show_details_{idx}']:
                        with st.spinner("Fetching details..."):
                            details = get_movie_details(movie['id'])
                            time.sleep(0.5)  # Small delay between requests
                        
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Year:**", details['year'])
                            st.write("**Rating:**", details['rating'])
                            st.write("**Duration:**", details['duration'])
                        
                        with col2:
                            st.write("**Director:**", details['director'])
                        
                        st.write("**Plot:**")
                        st.write(details['plot'])
                        st.markdown("---")
        else:
            st.warning("No movies found matching your search. Please try a different search term.")

if __name__ == "__main__":
    main() 