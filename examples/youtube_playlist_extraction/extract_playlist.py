# @markdown ## Provide a thread url, playlist type, and url structure. Press the play button the left to generate!
thread = "https://forum.mafiascum.net/viewtopic.php?t=91822"  # @param {type:"string"}
playlist_type = "regular videos"  # @param ["music", "regular videos"]
try_to_shorten_playlist_url = False  # @param {type:"boolean"}

from donbot.operations import get_posts, get_thread_page_urls
import requests
from lxml import html


def extract_youtube_links(post_content: str):
    "Return all links to youtube videos in the post content"

    clean_youtube_links = []
    for link_path in ["//iframe/@src", "//a/@href"]:
        for link in html.fromstring(post_content).xpath(link_path):
            if "list" in link:
                continue
            if "youtube" not in link and "youtu.be" not in link:
                continue
            video_id = link.split("/")[-1]
            clean_youtube_links.append(f"https://www.youtube.com/watch?v={video_id}")
    return clean_youtube_links


def create_playlist_url(video_links: list[str]):
    "Return a youtube playlist url from a list of video links"
    
    video_ids = []
    for link in video_links:
        video_id = link.split("v=")[1]
        if video_id not in video_ids:
            video_ids.append(video_id)
    return f"http://www.youtube.com/watch_videos?video_ids={','.join(video_ids)}"


if __name__ == "__main__":

    session = requests.Session()
    thread_html = html.fromstring(session.get(thread).content)
    thread_urls = get_thread_page_urls(thread, thread_html)

    posts = []
    for thread_url in thread_urls:
        thread_page_html = html.fromstring(session.get(thread_url).content)
        posts.extend(get_posts(thread_page_html))
    
    first_user_contents = [post["content"] for post in posts if post["user"] == posts[0]["user"]]
    youtube_links = sum(
        (extract_youtube_links(content) for content in first_user_contents), []
    )
    for i in range(0, len(youtube_links), 50):
        youtube_links_subset = youtube_links[i:min(i + 50, len(youtube_links))]
        playlist_url = create_playlist_url(youtube_links_subset)
        if try_to_shorten_playlist_url:
            playlist_url = session.get(playlist_url).url

        print('Playlist URL:')
        if playlist_type == 'music':
            print(playlist_url.replace('www', 'music'))
        else:
            print(playlist_url)