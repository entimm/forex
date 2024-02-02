from flask import Blueprint, request

blueprint = Blueprint('metatrade', __name__)


@blueprint.route('/metatrade', methods=['POST'])
def metatrade():
    raw_data = request.get_data()
    print("收到:", str(raw_data))

    return 'Request body received'
