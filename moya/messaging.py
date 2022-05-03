import requests

class API:
    def __init__(self, token, base_url="https://api.moya.app"):
        """
        token: The business API token for your account
        """
        super().__init__()
        if not token:
            raise Exception("No token passed")
        if len(token) < 15:
            raise Exception("Invalid token passed")

        self.token = token
        self.base_url = base_url
        self.session = requests.Session()

    def request(self, path, content=None, params={}, action="post", files=[]):
        extra_args = {}
        if content:
            extra_args["json"] = content
        if files:
            extra_args['files'] = files
        fn = getattr(self.session, action)
        path = f"{self.base_url}/v1/{path}"
        r = fn(path, params=params, headers={"Authorization": f"Bearer {self.token}"}, **extra_args)
        r.raise_for_status()
        return r

    def generate_send_text_body(self, to, body, recipient_type="individual", priority="low"):
        return {
            'recipient_type': recipient_type,
            'type': 'text',
            'to': to,
            'priority': priority,
            'text': { 'body' : body }
        }

    def send_message(self, to, text : str, priority="medium", job_id=None):
        """
        https://docs.moya.app/#sending-messages

        Send a text message to a set of users

        to: number or array of numbers
        text: The text content of the message. See https://docs.moya.app/#formatting for details
        """
        body = self.generate_send_text_body(to, text, recipient_type='broadcast' if isinstance(to, list) else 'individual', priority=priority)
        params = {}
        if job_id:
            params['job_id'] = str(job_id)
        r = self.request("message", body, params)
        return r.json()

    def bulk_send_messages(self, messages, priority="medium", job_id=None):
        """
        https://docs.moya.app/#bulk-sending-messages

        Send a text message to a set of users

        messages: A list of tuples containing the number and the text content of the message to send.
        """
        body = []
        for to, text in messages:
            body.append(self.generate_send_text_body(to, text, recipient_type='individual', priority=priority))
        params = {}
        if job_id:
            params['job_id'] = str(job_id)
        r = self.request("messages", body, params)
        return r.json()

    def upload_image(self, image_fh):
        """
        https://docs.moya.app/#uploading-an-image

        Upload and optimize an image ready for distribution
        """
        r = self.request("upload_image", files=[('file', ('t.jpg', image_fh))])
        return r.json()["url"]

    def generate_send_image_body(self, to, image_url, recipient_type="individual", priority="medium"):
        return {
            'recipient_type': recipient_type,
            'type': 'image',
            'to': to,
            'priority': priority,
            'image': { 'url' : image_url }
        }

    def send_image(self, to, image_url, priority="medium", job_id=None):
        """
        https://docs.moya.app/#sending-the-image-to-a-user

        Send an image to a set of users

        to: number or array of numbers
        image_url: The url for the image. Must have been returned by upload_image() above
        """
        body = self.generate_send_image_body(to, image_url, recipient_type='broadcast' if isinstance(to, list) else 'individual', priority=priority)
        params = {}
        if job_id:
            params['job_id'] = str(job_id)

        return self.request("message", body, params)

    def lookup_user(self, lookup):
        """
        https://docs.moya.app/#individual-user-lookups

        Return data about a given user based on phone number or Moya DID

        lookup: Phone number (eg 2701234567) or Moya DID (eg e5b1de4f-8acd-4a8a-b30b-b38b58543b5a)
        """
        r = self.request(f'users/{lookup}', action="get")
        return r.json()["user_profile"]

    def lookup_numbers(self, numbers, hashed=False):
        """
        https://docs.moya.app/#bulk-contact-lookups

        Given a list of numbers, return the ones which are in Moya
        """
        if not numbers:
            return []
        if len(numbers) > 3000:
            raise Exception("Too many numbers to be able to look up in one go")
        params = {"contacts": numbers}
        if hashed:
            params["hashed"] = True
        r = self.request("contacts", params)
        return r.json()["match_list"]

    def cancel_job(self, job_id):
        """
        https://docs.moya.app/#cancelling-in-progress-sending

        Cancel a given job
        """
        self.request(f"jobs/{job_id}", action="delete")

    def get_configuration(self):
        """
        https://docs.moya.app/#configuration

        Get and print the configuration of the account
        """
        r = self.request("configuration", action="get")
        return r.json()['configuration']

    def get_avatar(self):
        """
        https://docs.moya.app/#avatar-image

        Get and save the avatar of the account
        """
        r = self.request("avatar", action="get")
        return r.content

    def modify_avatar(self, file):
        """
        https://docs.moya.app/#avatar-image

        Create or Modify Avatar
        """
        r = self.request("avatar", action="put", files=[('file', ('avatar.png', file))])
        return r.json

