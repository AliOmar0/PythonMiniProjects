import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json
from datetime import datetime

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
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # Find all search result items (limit to first 5)
        for item in list(soup.select('li.ipc-metadata-list-summary-item'))[:5]:
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        script_tag = soup.find('script', {'type': 'application/json', 'id': '__NEXT_DATA__'})
        
        if script_tag:
            json_data = json.loads(script_tag.string)
            try:
                movie_data = json_data['props']['pageProps']['mainColumnData']
            except Exception as e:
                try:
                    movie_data = json_data['props']['pageProps']['aboveTheFoldData']
                except Exception as e:
                    return {
                        'title': "Error",
                        'rating': "N/A",
                        'year': "N/A",
                        'duration': "N/A",
                        'director': "N/A",
                        'genres': "N/A",
                        'plot': "Could not fetch movie details"
                    }
            
            details = {}
            
            # Extract title
            try:
                details['title'] = movie_data.get('titleText', {}).get('text') or movie_data.get('originalTitleText', {}).get('text', 'N/A')
            except:
                details['title'] = 'N/A'
            
            # Extract rating and votes
            try:
                rating = None
                total_votes = None
                
                rating_summary = movie_data.get('ratingsSummary', {})
                if isinstance(rating_summary, dict):
                    rating = rating_summary.get('aggregateRating')
                    total_votes = rating_summary.get('voteCount')
                
                if not rating:
                    rating_elem = soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating__score"]')
                    if rating_elem:
                        rating_span = rating_elem.select_one('span')
                        if rating_span:
                            try:
                                rating = float(rating_span.text.strip())
                            except:
                                pass
                    
                    if rating and not total_votes:
                        votes_elem = soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating__score"] + div')
                        if votes_elem:
                            votes_text = votes_elem.text.strip()
                            votes_match = re.search(r'([\d,]+)', votes_text)
                            if votes_match:
                                try:
                                    total_votes = int(votes_match.group(1).replace(',', ''))
                                except:
                                    pass
                
                release_date = movie_data.get('releaseDate', {})
                
                if release_date and isinstance(release_date, dict):
                    release_day = release_date.get('day')
                    release_month = release_date.get('month')
                    release_year = release_date.get('year')
                    
                    if all([release_day, release_month, release_year]):
                        movie_date = datetime(release_year, release_month, release_day)
                        if movie_date > datetime.now():
                            month_name = datetime(2000, release_month, 1).strftime('%B')
                            details['rating'] = f"Coming {month_name} {release_day}, {release_year}"
                        elif rating:
                            details['rating'] = f"{rating}/10 ({total_votes:,} votes)" if total_votes else f"{rating}/10"
                        else:
                            details['rating'] = "Rating not available"
                    elif release_year and int(release_year) > datetime.now().year:
                        details['rating'] = f"Coming in {release_year}"
                    elif rating:
                        details['rating'] = f"{rating}/10 ({total_votes:,} votes)" if total_votes else f"{rating}/10"
                    else:
                        details['rating'] = "Rating not available"
                elif rating:
                    details['rating'] = f"{rating}/10 ({total_votes:,} votes)" if total_votes else f"{rating}/10"
                else:
                    details['rating'] = "Rating not available"
            except Exception as e:
                details['rating'] = 'Rating not available'
            
            # Extract year
            try:
                year = movie_data.get('releaseYear', {}).get('year') or movie_data.get('releaseDate', {}).get('year')
                details['year'] = str(year) if year else "N/A"
            except:
                details['year'] = 'N/A'
            
            # Extract duration
            try:
                runtime_data = movie_data.get('runtime', {})
                if isinstance(runtime_data, dict):
                    seconds = runtime_data.get('seconds')
                    if seconds:
                        hours = seconds // 3600
                        minutes = (seconds % 3600) // 60
                        if hours > 0:
                            details['duration'] = f"{hours}h {minutes}m"
                        else:
                            details['duration'] = f"{minutes}m"
                    else:
                        details['duration'] = "N/A"
                else:
                    details['duration'] = "N/A"
            except:
                details['duration'] = 'N/A'
            
            # Extract director(s)
            try:
                directors = []
                directors_data = movie_data.get('directors', [])
                if isinstance(directors_data, list):
                    for director_item in directors_data:
                        if isinstance(director_item, dict):
                            credits = director_item.get('credits', [])
                            for credit in credits:
                                if isinstance(credit, dict) and credit.get('name'):
                                    name = credit.get('name', {}).get('nameText', {}).get('text')
                                    if name:
                                        directors.append(name)
                
                details['director'] = ', '.join(directors) if directors else "N/A"
            except:
                details['director'] = 'N/A'
            
            # Extract genres
            try:
                genres = []
                # Try to get genres from JSON data
                genres_data = movie_data.get('genres', {}).get('genres', [])
                if isinstance(genres_data, list):
                    for genre in genres_data:
                        if isinstance(genre, dict) and genre.get('text'):
                            genres.append(genre['text'])
                
                # If no genres found in JSON, try alternate JSON path
                if not genres:
                    genres_data = movie_data.get('titleGenres', {}).get('genres', [])
                    if isinstance(genres_data, list):
                        for genre in genres_data:
                            if isinstance(genre, dict) and genre.get('text'):
                                genres.append(genre['text'])
                
                # If still no genres, try HTML fallback
                if not genres:
                    genres_elem = soup.select('a.ipc-chip--on-baseAlt')
                    if genres_elem:
                        genres = [genre.text.strip() for genre in genres_elem]
                
                details['genres'] = ', '.join(genres) if genres else "N/A"
            except:
                details['genres'] = 'N/A'
            
            # Extract plot
            try:
                plot = None
                plot_sources = {
                    'plot': movie_data.get('plot'),
                    'plotOutline': movie_data.get('plotOutline'),
                    'plotSummary': movie_data.get('plotSummary'),
                    'plotSummaries': movie_data.get('plotSummaries', []),
                    'synopses': movie_data.get('synopses', []),
                    'outlines': movie_data.get('outlines', []),
                    'reviews': movie_data.get('featuredReviews', []),
                    'overview': movie_data.get('overview', {}),
                    'summaries': movie_data.get('summaries', [])
                }
                
                # Try main plot
                if not plot and plot_sources['plot']:
                    plot_obj = plot_sources['plot']
                    if isinstance(plot_obj, dict):
                        plot = (plot_obj.get('plotText', {}).get('plainText') or
                               plot_obj.get('outline', {}).get('text') or
                               plot_obj.get('text'))
                
                # Try plot outline
                if not plot and plot_sources['plotOutline']:
                    plot_outline = plot_sources['plotOutline']
                    if isinstance(plot_outline, dict):
                        plot = plot_outline.get('text')
                
                # Try plot summary
                if not plot and plot_sources['plotSummary']:
                    plot_summary = plot_sources['plotSummary']
                    if isinstance(plot_summary, dict):
                        plot = plot_summary.get('text')
                
                # Try plot summaries array
                if not plot and plot_sources['plotSummaries']:
                    for summary in plot_sources['plotSummaries']:
                        if isinstance(summary, dict) and summary.get('text'):
                            plot = summary.get('text')
                            break
                
                # Try synopses array
                if not plot and plot_sources['synopses']:
                    for synopsis in plot_sources['synopses']:
                        if isinstance(synopsis, dict) and synopsis.get('text'):
                            plot = synopsis.get('text')
                            break
                
                # Try overview
                if not plot and isinstance(plot_sources['overview'], dict):
                    plot = plot_sources['overview'].get('plotSummary', {}).get('text')
                
                # Try summaries
                if not plot and plot_sources['summaries']:
                    for summary in plot_sources['summaries']:
                        if isinstance(summary, dict) and summary.get('text'):
                            plot = summary.get('text')
                            break
                
                # If still no plot, try the HTML fallback
                if not plot:
                    plot_elem = soup.select_one('span[data-testid="plot-xl"]')
                    if not plot_elem:
                        plot_elem = soup.select_one('span[data-testid="plot-l"]')
                    if not plot_elem:
                        plot_elem = soup.select_one('p[data-testid="plot"]')
                    if plot_elem:
                        plot = plot_elem.text.strip()
                
                # For upcoming movies, try to get synopsis from other sources
                if not plot:
                    release_date = movie_data.get('releaseDate', {})
                    if release_date and isinstance(release_date, dict):
                        release_year = release_date.get('year')
                        release_month = release_date.get('month')
                        release_day = release_date.get('day')
                        
                        if all([release_year, release_month, release_day]):
                            movie_date = datetime(release_year, release_month, release_day)
                            if movie_date > datetime.now():
                                plot = f"'{movie_data['titleText']['text']}' is an upcoming movie directed by {details.get('director', 'N/A')}."
                                if movie_data.get('productionStatus', {}).get('text'):
                                    plot += f" Current status: {movie_data['productionStatus']['text']}."
                
                details['plot'] = plot if plot else "Plot details are not available."
                
            except Exception as e:
                details['plot'] = 'Plot details are not available.'
            
            return details
        else:
            # Fallback to HTML scraping
            details = {}
            try:
                # Get title
                title_elem = soup.select_one('h1[data-testid="hero__pageTitle"]')
                details['title'] = title_elem.text.strip() if title_elem else "N/A"
                
                # Get rating
                rating_elem = soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating"]')
                if rating_elem:
                    rating_text = rating_elem.text.strip()
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
                metadata_items = soup.find_all('div', class_='sc-fa02f843-0')
                for item in metadata_items:
                    if 'Director' in item.text:
                        links = item.find_all('a')
                        if links:
                            director = ', '.join([link.text.strip() for link in links])
                            break
                details['director'] = director if director else "N/A"
                
                # Get genres
                genres = []
                genres_elem = soup.select('a.ipc-chip--on-baseAlt')
                if not genres_elem:
                    genres_elem = soup.select('span.ipc-chip__text')
                if genres_elem:
                    genres = [genre.text.strip() for genre in genres_elem]
                details['genres'] = ', '.join(genres) if genres else "N/A"
                
                # Get plot
                plot_elem = soup.select_one('span[data-testid="plot-xl"]')
                if not plot_elem:
                    plot_elem = soup.select_one('span[data-testid="plot-l"]')
                if not plot_elem:
                    plot_elem = soup.select_one('p[data-testid="plot"]')
                details['plot'] = plot_elem.text.strip() if plot_elem else "N/A"
                
                return details
            except Exception as e:
                st.error(f"Error in HTML fallback: {str(e)}")
                return {
                    'title': "Error",
                    'rating': "N/A",
                    'year': "N/A",
                    'duration': "N/A",
                    'director': "N/A",
                    'genres': "N/A",
                    'plot': "Could not fetch movie details"
                }
            
    except Exception as e:
        st.error(f"Error getting movie details: {str(e)}")
        return {
            'title': "Error",
            'rating': "N/A",
            'year': "N/A",
            'duration': "N/A",
            'director': "N/A",
            'genres': "N/A",
            'plot': "Could not fetch movie details"
        }

def main():
    st.title("Movie Information Scraper")
    st.write("Search for movies and get detailed information from IMDB")
    
    # Search box
    search_query = st.text_input("Enter movie title to search:")
    
    # Reset view states when a new search is performed
    if 'last_search' not in st.session_state:
        st.session_state.last_search = ''
    
    if search_query != st.session_state.last_search:
        # Clear all view states when search query changes
        for key in list(st.session_state.keys()):
            if key.startswith('show_details_'):
                del st.session_state[key]
        st.session_state.last_search = search_query
    
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
                            st.write("**Genres:**", details['genres'])
                        
                        st.write("**Plot:**")
                        st.write(details['plot'])
                        st.markdown("---")
        else:
            st.warning("No movies found matching your search. Please try a different search term.")

if __name__ == "__main__":
    main() 