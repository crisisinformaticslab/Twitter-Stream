import requests
import os
import json


# This is a modified code from twitter API v2 sample.

# header maker
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


# Get all rules from one developer's account
def get_rules(headers):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    #    print(json.dumps(response.json()))
    return response.json()


# Delete all rules in case we want to test something new. Otherwise this can be used to delete individual rule/request
def delete_all_rules(headers, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )


# This is actually how we send the requests to twitter.
def set_rules(headers, query, tag):
    rules = [
        {"value": query, "tag": tag}
    ]
    payload = {"add": rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code >= 500:
        return (
            "We encounter an issue with Twitter server, please try again later", response.json()
        )
    elif response.status_code == 201:
        return response.json()
    else:
        return (
            "Request is rejected, please verify your input and try again later", response.json()
        )


# I know what you are thinking, it is here for testing purpose. Do not rely on this function to get stream since it
# requires a persistent connection to twitter server in which lambda will time out before that even finish.
def get_stream(headers, stream_id):
    # Tone down your additional fieds, you may not need all these.
    additional_fields = "tweet.fields=attachments%2Cauthor_id%2Ccontext_annotations%2Cconversation_id%2Ccreated_at%2Centities%2Cgeo%2Cid%2Cin_reply_to_user_id%2Clang%2Cpublic_metrics%2Cpossibly_sensitive%2Creferenced_tweets%2Creply_settings%2Csource%2Ctext%2Cwithheld&user.fields=created_at%2Cdescription%2Centities%2Cid%2Clocation%2Cname%2Cpinned_tweet_id%2Cprofile_image_url%2Cprotected%2Cpublic_metrics%2Curl%2Cusername%2Cverified%2Cwithheld&expansions=attachments.poll_ids%2Cattachments.media_keys%2Cauthor_id%2Centities.mentions.username%2Cgeo.place_id%2Cin_reply_to_user_id%2Creferenced_tweets.id%2Creferenced_tweets.id.author_id"
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?" + additional_fields, headers=headers, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print(json.dumps(json_response, indent=4, sort_keys=True))
