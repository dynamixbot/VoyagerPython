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
        return jsonify(
            {
                "error": "CategoryNotFoundError",
                "message": "Valid categories are: " + str(list(r_category_ids().keys())),   
            }
        )
    response = requests.get(
        f"https://scratch.mit.edu/discuss/{id}?page={page}", timeout=10
    )
    soup = bs4.BeautifulSoup(response.content, "html.parser")

    # Create an empty list to store topic information
    topics = []

    # Find all the post elements
    post_elements = soup.find_all("h3", class_="topic_isread")
    print(str(post_elements))
    # Loop through each post element and extract the relevant information
    for post_element in post_elements:
        post_id = post_element.a["href"].split("/")[-2]
        post_title = post_element.a.get_text()
        post_author = post_element.find_next_sibling("span", class_="byuser").get_text()[3:]

        # Append the extracted information to the topics list as a dictionary
        topics.append({"id": post_id, "title": post_title, "author": post_author})

    # Return the topics list as a JSON response
    return jsonify(topics)


if __name__ == "__main__":
    app.run()
