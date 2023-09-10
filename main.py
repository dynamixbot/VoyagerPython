from flask import Flask, render_template, request, jsonify
import requests
import bs4

from utils import r_category_ids

app = Flask("Voyager")

# Define a constant for the number of pages to retrieve (e.g., 2)
NUM_PAGES_TO_RETRIEVE = 2

@app.get("/")
def home():
    return render_template("home.html")

@app.get("/v1/forum/category/topics/<category>/<page>")
def topic_list(category, page):
    args = request.args.to_dict()
    # detail = args.get("detail", "0")
    print(str(args))
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
    # Create an empty list to store topic information
    topics = []

    # Helper function to check if a post is closed
    def is_closed(post_id):
        if post_id in closed_posts:
            return "1"
        else:
            return "0"

    # Helper function to check if a post is sticky
    def is_sticky(post_id):
        if post_id in sticky_posts:
            return "1"
        else:
            return "0"

    # Loop through each page and retrieve topics
    for i in range(int(page), int(page) + 1):
        try:
            response = requests.get(
                f"https://scratch.mit.edu/discuss/{id}?page={i}", timeout=10
            )
            soup = bs4.BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.Timeout:
            return (
                jsonify(
                    {
                        "error": "RequestTimeoutError",
                        "message": "The request timed out. Please try again.",
                    }
                ),
                504,
            )
        # Check if the page has topics
        msg = soup.find("td", class_="djangobbcon1")
        if msg and msg.text.strip() == "Forum is empty.":
            break

        # Find all the post elements
        post_elements = soup.find_all("h3", class_="topic_isread")
        closed_post_divs = soup.find_all("div", class_="iclosed")
        sticky_post_divs = soup.find_all("div", class_="isticky")
        closed_posts = []
        sticky_posts = []
        for closed_div in closed_post_divs:
            # Extract the post URL
            post_url = closed_div.find_parent("tr").find("h3").a["href"]
            # Extract the post ID from the URL
            post_id = post_url.split("/")[-2]
            # Append the post ID to the list of closed posts
            closed_posts.append(post_id)

        for sticky_div in sticky_post_divs:
            # Extract the post URL
            post_url = sticky_div.find_parent("tr").find("h3").a["href"]
            # Extract the post ID from the URL
            post_id = post_url.split("/")[-2]
            # Append the post ID to the list of sticky posts
            sticky_posts.append(post_id)

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
    app.run(debug=True)
