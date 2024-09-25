import requests
import xml.etree.ElementTree as ET
import json
import re
import os
from urllib.parse import urlparse

def get_rss_from_apple_podcasts(apple_url, manual_id=None):
    print(f"Fetching RSS feed from Apple Podcasts URL: {apple_url}")
    if manual_id:
        podcast_id = manual_id
        print(f"Using manually provided podcast ID: {podcast_id}")
    else:
        match = re.search(r'id(\d+)', apple_url)
        if not match:
            print("Failed to extract podcast ID from the URL")
            return None
        podcast_id = match.group(1)
        print(f"Extracted podcast ID: {podcast_id}")

    api_url = f"https://itunes.apple.com/lookup?id={podcast_id}&entity=podcast"
    print(f"Fetching podcast details from iTunes API: {api_url}")
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"Failed to fetch podcast details. Status code: {response.status_code}")
        return None

    data = json.loads(response.text)
    if not data['results']:
        print("No results found in the API response")
        return None

    rss_url = data['results'][0].get('feedUrl')
    print(f"Retrieved RSS feed URL: {rss_url}")
    return rss_url

def get_latest_episode_link(rss_url):
    print(f"Fetching RSS feed from URL: {rss_url}")
    response = requests.get(rss_url)
    
    if response.status_code != 200:
        print(f"Failed to fetch the RSS feed. Status code: {response.status_code}")
        return None

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")
        return None

    latest_episode = root.find(".//item")
    
    if latest_episode is None:
        print("No episodes found in the RSS feed")
        return None

    enclosure = latest_episode.find("enclosure")
    
    if enclosure is not None and 'url' in enclosure.attrib:
        mp3_url = enclosure.attrib['url']
        print(f"Found MP3 URL: {mp3_url}")
        return mp3_url
    else:
        print("No audio link found for the latest episode")
        return None

def download_episode(mp3_url):
    print(f"Downloading episode from URL: {mp3_url}")
    response = requests.get(mp3_url, stream=True)
    
    if response.status_code != 200:
        print(f"Failed to download the episode. Status code: {response.status_code}")
        return False

    # Extract filename from URL
    filename = os.path.basename(urlparse(mp3_url).path)
    if not filename.endswith('.mp3'):
        filename += '.mp3'

    # Save the file
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Episode downloaded successfully: {filename}")
    return True

def main():
    apple_podcasts_url = "https://podcasts.apple.com/ee/podcast/agor%C3%BCtm/id1486754329"
    manual_podcast_id = "1486754329"  # Correct ID for Agorütm podcast

    rss_url = get_rss_from_apple_podcasts(apple_podcasts_url, manual_podcast_id)

    if rss_url:
        print(f"RSS feed URL: {rss_url}")
        latest_episode_link = get_latest_episode_link(rss_url)
        if latest_episode_link:
            print(f"Link to the latest episode MP3: {latest_episode_link}")
            if download_episode(latest_episode_link):
                print("Download completed successfully.")
            else:
                print("Failed to download the episode.")
        else:
            print("Failed to retrieve the latest episode link.")
    else:
        print("Failed to retrieve the RSS feed URL from Apple Podcasts.")

    print("Script execution completed.")

if __name__ == "__main__":
    main()
