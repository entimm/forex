from flask import request


def make_cache_key():
    return request.path, frozenset(request.args.items())
