from flask import Flask, render_template, request, jsonify
import requests
import bs4

from utils import r_category_ids

app = Flask("Voyager")


@app.get("/")
def home():
    return render_template("home.html")


@app.get("/v1/forum/category/topics/<category>/<page>")
def topic_list(category, page):
    args = request.args.to_dict()
    try:
        id = r_category_ids()[category]
    except KeyError:
        return (
            jsonify(
                {
                    "error": "CategoryNotFoundError",
                    "message": "Valid categories are: "
                    + str(list(r_category_ids().keys())),
                }
            ),
            400,
        )
    response = requests.get(
        f"https://scratch.mit.edu/discuss/{id}?page={page}", timeout=10
    )
    soup = bs4.BeautifulSoup(response.content, "html.parser")

    msg = soup.find("td", class_="djangobbcon1")
    if msg and msg.text.strip() == "Forum is empty.":
        return (
            jsonify(
                {
                    "error": "NoMoreTopicsError",
                    "message": "There are no more topics on that page.",
                }
            ),
            400,
        )

    # Create an empty list to store topic information
    topics = []

    # Find all the post elements
    post_elements = soup.find_all("h3", class_="topic_isread")
    closed_post_divs = soup.find_all("div", class_="iclosed")
    sticky_post_divs = soup.find_all("div", class_="isticky")
    closed_posts = []
    sticky_posts = []

    for closed_div in closed_post_divs:
        post_row = closed_div.find_parent("tr")

        # Extract the post URL
        post_url = post_row.find("h3").a["href"]

        # Extract the post ID from the URL (assuming it's the last part after the last '/')
        post_id = post_url.split("/")[-2]

        # Append the post ID to the list of closed posts
        if closed_div:
            closed_posts.append(post_id)
    for sticky_div in sticky_post_divs:
        post_row = sticky_div.find_parent("tr")

        # Extract the post URL
        post_url = post_row.find("h3").a["href"]

        # Extract the post ID from the URL
        post_id = post_url.split("/")[-2]

        # Append the post ID to the list of sticky posts
        if sticky_div:
            sticky_posts.append(post_id)

    def is_closed(post_id):
        if post_id in closed_posts:
            return "1"
        else:
            return "0"

    def is_sticky(post_id):
        if post_id in sticky_posts:
            return "1"
        else:
            return "0"

    # Loop through each post element and extract the relevant information
    for post_element in post_elements:
        post_id = post_element.a["href"].split("/")[-2]
        post_title = post_element.a.get_text()
        post_author = post_element.find_next_sibling(
            "span", class_="byuser"
        ).get_text()[3:]
        post_category = category
        # Append the extracted information to the topics list as a dictionary
        topics.append(
            {
                "id": post_id,
                "title": post_title,
                "author": post_author,
                "category": post_category,
                "closed": is_closed(post_id),
                "sticky": is_sticky(post_id),
            }
        )

    # Return the topics list as a JSON response
    return jsonify(topics)


if __name__ == "__main__":
    app.run()
