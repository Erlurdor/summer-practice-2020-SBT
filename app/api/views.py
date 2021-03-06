import bcrypt
import json
from uuid import uuid4
from app.database import db
from sqlalchemy.sql import func
from app import token_manager, addr_white_list
from datetime import datetime
from flask import (
    Blueprint,
    request,
    flash,
    abort,
    redirect,
    url_for,
    current_app,
    jsonify
)
from app.api.models import (
    User,
    PublicCollection,
    UserRoleInCollection,
    Post,
    RolesPermissions,
    Role,
    Permission
)

module = Blueprint('entity', __name__)


last_user_id = None


# Token generation function uses
# UUIDv4
def generateToken():
    return uuid4().hex


@module.route('/index', methods=['GET'])
def index():
    return 'Hello'


# COMPLETE
@module.route('/auth', methods=['POST'])
def auth():
    '''
    in
    {
        "login": "a1pha1337@gmail.com",
        "password": "rhokef3"
    }
    out
    token
    '''

    if not request.json or \
        not 'login' in request.json or \
        not 'password' in request.json:

        abort(400, 'Missed required arguments')

    login = request.json['login']
    password = request.json['password']

    # comp login/pass with data in db
    # if incorrect -> abort(401)
    temp_user = User.query.filter_by(login=login).first()
    if temp_user is None or \
        not bcrypt.checkpw(password.encode('utf8'), temp_user.password.encode('utf8')):

        abort(401, 'Login or password is incorrect')

    token = generateToken()

    token_manager.addTokenDirect(temp_user.id, token, datetime.now())

    return token, 200


# COMPLETE
@module.route('/logout/<string:token>', methods=['GET'])
def logout(token):
    '''
    in
    string
    out
    - 200 OK
    - 404 Non-existing token
    '''

    if isinstance(token, str):
        is_exist = token_manager.deleteToken(token)

        if not is_exist:
            abort(404, 'Non-existing token')

    else:
        abort(400, 'Bad request')

    return '', 200


# COMPLETE
@module.route('/validate/<token>', methods=['GET'])
def validate(token):
    '''
    in
    string
    out
    - 200 OK
    - 404 Non-existing token
    '''

    user_id = token_manager.getUserIdByToken(token)

    if user_id is None:
        abort(404, 'Non-existing token')

    token_manager.updateToken(token)

    return '', 200


# COMPLETE
@module.route('/user', methods=['POST'])
def userRegister():
    '''
    in
    {
        "login": "a1pha1337@gmail.com",
        "password": "rhokef3"
        "name": "a1pha1337"
    }
    out
    - 200
    token
    - 400 Incorrect login/pass
    '''
    
    # JSON body checking
    if not request.json or \
        not 'login' in request.json or \
        not 'password' in request.json or \
        not 'name' in request.json:

        abort(400, 'Missed required arguments')

    login = request.json['login']
    password = request.json['password']
    name = request.json['name']

    # Get from database user with same login
    duplicated_user = User.query.filter_by(login=login).first()

    # If user with same login exists abort
    if duplicated_user is not None:
        abort(409, 'Login already exists')

    global last_user_id

    # Initialize last_user_id
    if last_user_id is None:
        last_user_table_id = db.session.query(func.max(User.id)).scalar()
        if last_user_table_id is None:
            last_user_id = 0
        else:
            last_user_id = last_user_table_id

    last_user_id += 1

    # Hashing and salting password
    hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

    # Create new user
    new_user = User(id=last_user_id, login=login, password=hashed_password.decode('utf8'), name=name)

    # Add user information into database
    db.session.add(new_user)
    db.session.commit()
    token = generateToken()

    # Add token to tokenManager
    token_manager.addTokenDirect(last_user_id, token, datetime.now())

    return token, 200


@module.route('/user/delete/<token>', methods=['DELETE'])
def userDelete(token):
    '''
    in
    string
    out
    - 200 OK
    - 404 Non-existing token
    '''

    user_id = token_manager.getUserIdByToken(token)

    # If token doesn't exist
    if user_id is None:
        abort(404, 'Non-existing token')

    # Temporarily. In the future, transfer initialization and remove code below
    # global last_user_id

    # Initialize last_user_id
    # if last_user_id is None:
    #     last_user_table_id = db.session.query(func.max(User.id)).scalar()
    #     if last_user_table_id is None:
    #         last_user_id = 0
    #     else:
    #         last_user_id = last_user_table_id
    # End of temp code

    # last_user_id -= 1
    # logout all tokens with current user_id
    # for i in tokens:
    #     if i['user_id'] == user_id:
    #         tokens.pop(tokens.index(i))
    if isinstance(token, str):
        is_exist = token_manager.deleteToken(token)


    # Clean up db UserRoleInCollection
    user_role_in_collection = 'notNone'
    while user_role_in_collection is not None:
        user_role_in_collection = UserRoleInCollection \
                                .query \
                                .filter_by(user_id=user_id) \
                                .first()
        if user_role_in_collection is None:
            break
        db.session.delete(user_role_in_collection)
        db.session.commit()
    
    # Clean up db Post
    post = 'notNone'
    while post is not None:
        post = Post.query.filter_by(user_id=user_id).first()
        if post is None:
            break
        db.session.delete(post)
        db.session.commit()

    # Remove login from db. Decrement userId. return 200
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()

    return "Complete", 200


# COMPLETE
@module.route('/user/info/<token>', methods=['GET'])
def getUserInfoByToken(token):
    '''
    in
    string
    out
    - 200
    {
        "user_id": 0,
        "login": "alpha13371@mail.ru",
        "name": "Solo_228"
    }
    - 404 Non-existing token
    '''
    # valid token ?
    # yes -> get userId from token. Get login and password by userId. Add to Answer. Return Answer, 200
    # no -> return 404

    # Searching token in tokens list
    user_id = token_manager.getUserIdByToken(token)

    # If token doesn't exist
    if user_id is None:
        abort(404, 'Non-existing token')

    token_manager.updateToken(token)

    user = User.query.filter_by(id=user_id).first()

    info = {
        'user_id': user_id,
        'login': user.login,
        'name': user.name
    }

    return jsonify(info), 200


# COMPLETE
@module.route('/user/info/public/<login>', methods=['GET'])
def getUserInfoByLogin(login):
    '''
    in
    string
    out
    - 200
    {
        "user_id": 0,
        "login": "alpha13371@mail.ru",
        "name": "Solo_228"
    }
    - 404 Non-existing login
    '''
    user = User.query.filter_by(login=login).first()
    if user is None:
        abort(404, 'Non-existing login')

    info = {
        'user_id': user.id,
        'login': user.login,
        'name': user.name
    }

    return jsonify(info), 200


# COMPLETE
@module.route('/user/info', methods=['PUT'])
def editUserInfo():
    '''
    in
    {
        "token": "f57ebe597a3741b688269209fa29b053",
        "info": {
            "password": "rhokef3",
            "new_password": "123",
            "name": "Solo_322"
        }
    }
    out
    - 200
    - 400
    '''
    if not request.json or \
        not 'token' in request.json or \
        not 'info' in request.json:

        abort(400, 'Missed required arguments')

    # Request data
    token = request.json['token']
    info = request.json['info']

    # Searching token in tokens list
    user_id = token_manager.getUserIdByToken(token)

    # If token doesn't exist -> abort(404)
    if user_id is None:
        abort(404, 'Non-existing token')

    token_manager.updateToken(token)

    user = User.query.filter_by(id=user_id).first()

    # If user want to change pass, check with hash in db
    if 'password' in info and 'new_password' in info:
        password = info['password']
        new_password = info['new_password']

        if not bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8')):
            abort(401, 'Password is incorrect')

        user.password = bcrypt.hashpw(new_password.encode('utf8'), bcrypt.gensalt()).decode('utf8')

    # If user want to change name
    if 'name' in info:
        user.name = info['name']

    db.session.commit()

    return '', 200


# COMPLETE
@module.route('/permissions/userRole', methods=['POST'])
def setUserRole():
    '''
    in
    {
        "token": "f57ebe597a3741b688269209fa29b053",
        "collection_id": 228,
        "user_id": 5,
        "role_id": 30
    }
    out
    - 200: "OK"
    - 400: "Access error"
    - 404: "Non-existing token"
    '''
    if not request.json or not 'token' in request.json or \
        not 'collection_id' in request.json or \
        not 'user_id' in request.json or \
        not 'role_id' in request.json:

        abort(400, 'Missed required arguments')

    token = request.json['token']
    collection_id = request.json['collection_id']
    user_id_target = request.json['user_id']
    role_id = request.json['role_id']

    user_id_self = token_manager.getUserIdByToken(token)

    if user_id_self is None:
        abort(404, 'Non-existing token')

    token_manager.updateToken(token)

    user_target = User.query.filter_by(id=user_id_target).first()

    if user_target is None:
        abort(404, 'Non-existing user ID')

    # Check if role_id is incorrect
    # incorrect -> abort(404)
    role_in_collection_self = UserRoleInCollection \
                            .query \
                            .filter_by(user_id=user_id_self, collection_id=collection_id) \
                            .first()
    
    if role_in_collection_self is None:
        abort(404, 'User doesn\'t belong to this collection')

    if not UserRoleInCollection.query.filter_by(user_id=user_id_target).first() is None:
        abort(409, 'User already has role in collection')

    # Check if user_id_self are enough rights for
    # set current role_id to user_id_target
    # false -> abort(403, 'Not have enough permissions')    
    if role_in_collection_self.role_id < role_id:
        target_user_role_in_collection = UserRoleInCollection(
            collection_id=collection_id,
            role_id=role_id,
            user_id=user_id_target
        )

        db.session.add(target_user_role_in_collection)
        db.session.commit()
    else:
        abort(403, 'Not have enough permissions')
        
    return '', 200


# COMPLETE
# FIX SWAGGER API
@module.route('/permissions/userRole/<int:user_id>', methods=['GET'])
def getUserRole(user_id):
    '''
    in
    :user_id:
    out
    - 200
    [
        {
            collection_id: 228,
            role_id: 40
        }
        {
            collection_id: 322,
            role_id: 30
        }
    ]
    - 404: "Non-existing user ID"
    '''

    user = User.query.filter_by(id=user_id).first()

    if user is None:
        abort(404, 'Non-existing user ID')

    roles_in_collections = list()
    for user_role_in_collection in UserRoleInCollection.query.filter_by(user_id=user_id).all():
        roles_in_collections.append({
            'collection_id': user_role_in_collection.collection_id,
            'role_id': user_role_in_collection.role_id
        })

    return jsonify(roles_in_collections), 200


# COMPLETE
@module.route('/permissions/editUserRole', methods=['PUT'])
def editUserRole():
    '''
    in
    {
        "token": "f57ebe597jma3741b688269209fa29b053",
        "collection_id": 228,
        "user_id": 5,
        "role_id": 30
    }
    out
    - 200: "OK"
    - 403: "Not have enough permissions"
    - 404: "Non-existing token"
    - 404: "User doesn't belong to this collection"
    - 404: "Unknown role"
    '''
    if not request.json or \
        not 'token' in request.json or \
        not 'collection_id' in request.json or \
        not 'user_id' in request.json or \
        not 'role_id' in request.json:

        abort(400, 'Missed required arguments')

    token = request.json['token']
    collection_id = request.json['collection_id']
    target_user_id = request.json['user_id']
    target_role_id = request.json['role_id']

    user_id = token_manager.getUserIdByToken(token)

    if user_id is None:
        abort(404, 'Non-existing token')

    token_manager.updateToken(token)

    # Role existing checking
    role = Role.query.filter_by(id=target_role_id).first()
    if role is None:
        abort(404, 'Unknown role')

    # Check client permissions and belonging to collection
    user_collections_role = json.loads(getUserRole(user_id)[0].get_data())

    user_role_id = None
    for collection_role in user_collections_role:
        if collection_role['collection_id'] == collection_id:
            user_role_id = collection_role['role_id']
            break
    
    if user_role_id is None:
        abort(404, 'User doesn\'t belong to this collection')

    # Check target user existing and belonging to collection
    target_user_collections_role = json.loads(getUserRole(target_user_id)[0].get_data())

    target_user_role_id = None
    for collection_role in target_user_collections_role:
        if collection_role['collection_id'] == collection_id:
            target_user_role_id = collection_role['role_id']
            break

    if target_user_role_id is None:
        abort(404, 'User doesn\'t belong to this collection')

    # Checking client permissions (must be less or equal 20)
    # for editing others permissions
    if user_role_id > 20:
        abort(403, 'Not have enough permissions')
    # Moderator can't give admin or moderator permissions
    # elif user_role_id > 10 and target_user_role_id <= 20:
    elif user_role_id >= target_user_role_id:
        abort(403, 'Not have enough permissions')

    target_user_role_in_collection = UserRoleInCollection \
                                    .query \
                                    .filter_by(user_id=target_user_id, collection_id=collection_id) \
                                    .first()

    target_user_role_in_collection.role_id = target_role_id

    db.session.commit()

    return '', 200


# COMPLETE
@module.route('/permissions/role/<int:role_id>', methods=['GET'])
def getPermissionsByRole(role_id):
    '''
    in
    role_id
    out
    - 200:
    [
        'read',
        'rate',
        'write',
    ]
    - 404: "Unknown role"
    '''

    if Role.query.filter_by(id=role_id).first() is None:
        abort(404, 'Unknown role')

    permissions = [Permission.query.filter_by(id=roles_permissions.perm_id).first().name \
                for roles_permissions in RolesPermissions.query.filter_by(role_id=role_id).all()]


    return jsonify(permissions), 200


# COMPLETE
@module.route('/permissions/setPostOwner', methods=['POST'])
def setPostOwner():
    '''
    in
    {
        user_id: 42
        post_id: 3
    }
    out
    200:
        description: "OK"
    404:
        description: "Incorrect user_id/post_id"
    '''
    # JSON body checking
    if not request.json or \
            not 'user_id' in request.json or \
            not 'post_id' in request.json:
        abort(400, 'Missed required arguments')

    user_id = request.json['user_id']
    post_id = request.json['post_id']

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404, 'Incorrect user_id')

    post = Post.query.filter_by(post_id=post_id).first()
    if post is not None:
        abort(409, 'Current post already has owner')

    new_post = Post(post_id=post_id, user_id=user_id)

    # Add post into database
    db.session.add(new_post)
    db.session.commit()

    return '', 200


# COMPLETE
@module.route('/permissions/getPostOwner/<int:post_id>', methods=['GET'])
def getPostOwner(post_id):
    '''
    in
    post_id
    out
    - 200:
        4
    - 404:
        "Non-existing post"
    '''
    post = Post.query.filter_by(post_id=post_id).first()
    if post is None:
        abort(404, 'Non-existing post')


    return str(post.user_id), 200


@module.route('/permissions/removePublicCollection/<int:collection_id>', methods=['POST'])
def removePublicCollection(collection_id):
    '''
    in
    {
        token: df43f3rf34345452d2dfy3244
        collection_id: 322
    }
    out
    - 200
    - 400
    '''
    if not request.json or \
        not 'token' in request.json or \
        not 'collection_id' in request.json:

        abort(400, 'Missed required arguments')

    token = request.json['token']
    collection_id = request.json['collection']

    user_id = token_manager.getUserIdByToken(token)

    if user_id is None:
        abort(404, 'Non-existing token')

    token_manager.updateToken(token)

    user_collections_role = json.loads(getUserRole(user_id)[0].get_data())
    is_admin = False

    for current_collection_user_role in user_collections_role:
        if current_collection_user_role['collection_id'] == collection_id and \
                current_collection_user_role['role_id'] == 10:
            is_admin = True
    if not is_admin:
        abort(403, 'Not have enough permissions')

    # Finding public collection with same collection_id
    existing_public_collection = PublicCollection \
                                .query \
                                .filter_by(collection_id=collection_id) \
                                .first()

    # If collection already public, abort
    if not existing_public_collection:
        abort(409, 'Collection already private!')

    db.session.delete(existing_public_collection)
    db.session.commit()

    return '', 200


# COMPLETE
@module.route('/permissions/setPublicCollection', methods=['POST'])
def setPublicCollection():
    '''
    in
    {
        token: df43f3rf34345452d2dfy3244
        collection_id: 322
    }
    out
    - 200
    - 400
    '''
    if not request.json or \
        not 'token' in request.json or \
        not 'collection_id' in request.json:
        abort(400, 'Missed required arguments')

    token = request.json['token']
    collection_id = request.json['collection_id']

    user_id = token_manager.getUserIdByToken(token)

    if user_id is None:
        abort(404, 'Non-existing token')

    token_manager.updateToken(token)

    user_collections_role = json.loads(getUserRole(user_id)[0].get_data())

    is_admin = False

    for current_collection_user_role in user_collections_role:
        if current_collection_user_role['collection_id'] == collection_id and \
                current_collection_user_role['role_id'] == 10:
            is_admin = True
            break

    if not is_admin:
        abort(403, 'Not have enough permissions')

    # Finding public collection with same collection_id
    existing_public_collection = PublicCollection \
                                .query \
                                .filter_by(collection_id=collection_id) \
                                .first()

    # If collection already public, abort
    if existing_public_collection:
        abort(409, 'Collection already public!')

    # Create new public collection
    new_public_collection = PublicCollection(collection_id=collection_id)

    # Add new public collection into
    db.session.add(new_public_collection)
    db.session.commit()

    return '', 200


# COMPLETE
@module.route('/permissions/getPublicCollection', methods=['POST'])
def getPublicCollection():
    '''
    in
    [5, 7, 8, 12, 56]
    out
    - 200
    [12, 56]
    - 400
    '''

    if not request.json:
        abort(400)

    request_collections = request.json

    # Filter collections
    filtered_collections = [public_collection.collection_id for public_collection in PublicCollection.query \
                            if public_collection.collection_id in request_collections]

    return jsonify(filtered_collections), 200


# COMPLETE
@module.route('/permissions/getPublicCollection/all', methods=['GET'])
def getPublicCollectionAll():
    collections = [public_collection.collection_id for public_collection in PublicCollection.query]
    
    return jsonify(collections), 200


# COMPLETE
@module.route('/permissions/userRole/setCollectionOwner', methods=['POST'])
def setCollectionOwner():
    '''
    In:
    {
        "token": "f57ebe597a3741b688269209fa29b053",
        "collection_id": 228
    }
    Out:
    - 200: "Success"
    - 400: "Missed required arguments"
    - 409: "Collection already has owner"
    - 404: "Non-existing token"
    '''

    if not request.json or \
        not 'token' in request.json or \
        not 'collection_id' in request.json:

        abort(400, 'Missed required arguments')

    token = request.json['token']
    collection_id = request.json['collection_id']

    user_id = token_manager.getUserIdByToken(token)

    if user_id is None:
        abort(404, 'Non-existing token')

    token_manager.updateToken(token)

    # If collection already have owner -> abort(403)
    if not UserRoleInCollection \
            .query \
            .filter_by(collection_id=collection_id, role_id=10) \
            .first() is None:

        abort(409, 'Collection already has owner')

    collection_owner = UserRoleInCollection(user_id=user_id, collection_id=collection_id, role_id=10)

    db.session.add(collection_owner)
    db.session.commit()

    return '', 200


# If correct -> Need to add to API
# if post owner delete post -> clean up db Post
@module.route('/permissions/sync/ifPostDelete', methods=['POST'])
def ifPostDelete():
    '''
    in
    {
        "token": "f57ebe597a3741b688269209fa29b053",
        "post_id": 228
    }
    out
    200:
        description: "OK"
    403:
        description: 'Not have enough permissions'
    404:
        description: "Incorrect token/post_id"
    '''
    if not request.json or \
            not 'token' in request.json or \
            not 'post_id' in request.json:
        abort(400, 'Missed required arguments')

    token = request.json['token']
    post_id = request.json['post_id']
    
    user_id = token_manager.getUserIdByToken(token)
    if user_id is None:
        abort(404, 'Non-existing token')
    token_manager.updateToken(token)

    post = Post.query.filter_by(post_id=post_id).first()
    if post is None:
        abort(404, 'Non-existing post')

    if post.user_id != user_id:
        abort(403, 'Not have enough permissions')
    
    db.session.delete(post)
    db.session.commit()

    return '', 200


# If correct -> Need to add to API
# if admin delete collection -> clean up db PublicCollection and UserRoleInCollection
@module.route('/permissions/sync/ifCollectionDelete', methods=['POST'])
def ifCollectionDelete():
    '''
    in
    {
        "token": "f57ebe597a3741b688269209fa29b053",
        "collection_id": 228
    }
    out
    200:
        description: "OK"
    403:
        description: 'Not have enough permissions'
    404:
        description: "Incorrect post_id"
    '''
    if not request.json or \
            not 'token' in request.json or \
            not 'collection_id' in request.json:
        abort(400, 'Missed required arguments')

    token = request.json['token']
    collection_id = request.json['post_id']
    
    user_id = token_manager.getUserIdByToken(token)
    if user_id is None:
        abort(404, 'Non-existing token')
    token_manager.updateToken(token)

    user_collections_role = json.loads(getUserRole(user_id)[0].get_data())
    is_admin = False

    for current_collection_user_role in user_collections_role:
        if current_collection_user_role['collection_id'] == collection_id and \
                current_collection_user_role['role_id'] == 10:
            is_admin = True
    if not is_admin:
        abort(403, 'Not have enough permissions')

    existing_public_collection = PublicCollection \
                                .query \
                                .filter_by(collection_id=collection_id) \
                                .first()

    if existing_public_collection:
        db.session.delete(existing_public_collection)
        db.session.commit()
    
    # Clean up db UserRoleInCollection
    user_role_in_collection = 'notNone'
    while user_role_in_collection is not None:
        user_role_in_collection = UserRoleInCollection \
                                .query \
                                .filter_by(collection_id=collection_id) \
                                .first()
        if user_role_in_collection is None:
            break
        db.session.delete(user_role_in_collection)
        db.session.commit()

    return '', 200


# Reject all requests that not in
# white list
@module.before_request
def limitRemoteAddr():
    if addr_white_list:
        if not request.remote_addr in addr_white_list:
            abort(403)