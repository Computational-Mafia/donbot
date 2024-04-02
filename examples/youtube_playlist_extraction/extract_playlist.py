from donbot.operations import get_posts, get_thread_page_urls
import requests
from lxml import html


def extract_youtube_links(post_content: str):
    "Return all links to youtube videos in the post content"

    clean_youtube_links = []
    for link_path in ["//iframe/@src", "//a/@href"]:
        for link in html.fromstring(post_content).xpath(link_path):
            if "youtube" not in link and "youtu.be" not in link:
                continue
            video_id = link.split("/")[-1]
            clean_youtube_links.append(f"https://www.youtube.com/watch?v={video_id}")
    return clean_youtube_links


def create_playlist_url(video_links: list[str]):
    "Return a youtube playlist url from a list of video links"

    video_ids = [link.split("v=")[1] for link in video_links]
    return f"http://www.youtube.com/watch_videos?video_ids={','.join(video_ids)}"


if __name__ == "__main__":
    thread = "https://forum.mafiascum.net/viewtopic.php?t=91822" # @param {type:"string"}
    playlist_type = "regular videos" # @param ["music", "regular videos"]

    session = requests.Session()
    thread_html = html.fromstring(session.get(thread).content)
    thread_urls = get_thread_page_urls(thread, thread_html)

    posts = []
    for thread_url in thread_urls:
        thread_page_html = html.fromstring(session.get(thread_url).content)
        posts.extend(get_posts(thread_page_html))
    
    assert(len(posts) >= 144)
    first_user_contents = [post["content"] for post in posts if post["user"] == posts[0]["user"]]
    youtube_links = sum(
        (extract_youtube_links(content) for content in first_user_contents), []
    )
    playlist_url = create_playlist_url(youtube_links)
    final_playlist_url = session.get(playlist_url).url

    print('Playlist URL:')
    if playlist_type == 'music':
        print(final_playlist_url.replace('www', 'music'))
    else:
        print(final_playlist_url)