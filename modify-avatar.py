import argparse

from moya.messaging import API
from moya.argtypes import setup_argparse

parser = setup_argparse("Create/Modify Avatar", include_priority=False)
parser.add_argument("file", type=argparse.FileType('rb'), help="Avatar image file to upload")
args = parser.parse_args()

api = API(args.token, args.endpoint)
api.modify_avatar(args.file)
