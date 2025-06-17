import requests
import json
import ast


class Youtube:

    def auto_complete(self, query: str) -> list:
        """
        Fetching autocomplete results

        Args:
                query: str

        Returns:
                suggests:list # It will be return suggesstions as lst
        """
        apiUrl = "https://suggestqueries-clients6.youtube.com/complete/search"
        params = {"q": query, "client": "youtube"}
        try:
            response = requests.get(apiUrl,params=params)
        except Exception as e:
            return {"error": e}

        if not response.ok:
            return {"error": f"Bad status:{response.status}"}
        htmlPage = response.text
        try:
            suggests = [suggest[0] for suggest in ast.literal_eval(htmlPage[19:-1])[1]]
        except SyntaxError as e:
            return {"error": e}
        return suggests

    def info(self, videoId: str) -> dict:
        """
        Fetching metadata from video id

        Args:
                videoId: str

        Returns:
                result: dict # It will be return video metadata as dict
        """
        result = {}
        videoUrl = f"https://www.youtube.com/watch"
        try:
            response = requests.get(videoUrl,params={'v':videoId})
        except Exception as err:
            return {"error": err}

        if not response.ok:
            return {"error": f"Bad status code:{response.status_code}"}

        htmlPage = response.text
        try:
            json_data = (
                htmlPage.split("ytInitialPlayerResponse = ")[1].split("};")[0] + "}"
            )
        except Exception as err:
            return {"error": f"Error while parsing json: {err}"}
        try:
            data = json.loads(json_data)
        except Exception as err:
            return {"error": f"Error while turning json to dict:{err}"}

        videoDetails = data.get("videoDetails",'')
        if not videoDetails:
            return {}
        playerMicroformatRenderer = data["microformat"]["playerMicroformatRenderer"]

        videoDetailsKeys = [
            "author",
            "videoId",
            "title",
            "shortDescription",
            "keywords",
            "thumbnail",
            "channelId",
            "lengthSeconds",
            "viewCount",
        ]

        playerMicroformatRendererKeys = ["uploadDate", "likeCount", "category"]

        for key in videoDetailsKeys:
            result[key] = videoDetails.get(key)

        for key in playerMicroformatRendererKeys:
            result[key] = playerMicroformatRenderer.get(key)

        return result
