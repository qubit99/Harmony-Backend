import datetime

from flask_restful import Resource
from flask import Flask, request, jsonify, make_response

from harmony.models.user import UserAccount, UserPreference, SexualOrientation, Passions, UserPassions, UserImages, \
    UserSwipes, UserNotificationFeed, NotificationType, UserMatches
from harmony.resources.auth import token_required
from harmony import db
import tekore as tk
import requests

HRS_BASE_URL = "http://harmony-mrs.herokuapp.com"


class UserSettings(Resource):
    # method_decorators = [token_required]

    @token_required
    def get(self, user):
        request_data = request.args

        preference = UserPreference.query.filter_by(user_id=user.id).first()

        if user.sexual_orientation_id:
            sexual_orientation = SexualOrientation.query.get(user.sexual_orientation_id)
            if not sexual_orientation:
                return make_response(jsonify({'message': "Wrong Preference ID", 'success': False}), 400)
        else:
            sexual_orientation = None
        sexual_orientation_list = SexualOrientation.query.all()
        sexual_orientations = []
        for orientation in sexual_orientation_list:
            sexual_orientations.append({'name': orientation.name, 'id': orientation.id})
        print(preference)

        # passions
        passion_list = Passions.query.all()
        passions = [{'passion_id': passion.id, 'passion_name': passion.name} for passion in Passions.query.all()]
        User_passions_list = UserPassions.query.filter_by(user_id=user.id).all()
        User_passions = []
        for passion in User_passions_list:
            User_passions.append({'passion_id': passion.passion_id})

        data = {
            'name': user.f_name,
            'bio': user.bio,
            'job': user.job,
            'gender': user.gender,
            'birth_date': user.birth_date,
            'age_min': preference.age_min if preference else None,
            'age_max': preference.age_max if preference else None,
            'interested_gender': preference.interested_gender if preference else None,
            'sexual_orientation_name': sexual_orientation.name if sexual_orientation else None,
            'sexual_orientation_id': sexual_orientation.id if sexual_orientation else None,
            'sexual_orientation_list': sexual_orientations,
            'passion_list': passions,
            'user_passions': User_passions,
            'ytmusic_link': user.ytmusic_link,
            'spotify_link': user.spotify_link
        }
        return make_response(jsonify({'success': True, 'data': data}), 200)

    @token_required
    def post(self, user):

        request_data = request.get_json()
        track_ids = []
        if not user:
            return jsonify({'message': "Wrong user id given", 'success': False}), 404
        if 'name' in request_data:
            user.f_name = request_data['name']
        if 'bio' in request_data:
            user.bio = request_data['bio']
        if 'gender' in request_data:
            user.gender = request_data['gender']
        if 'job' in request_data:
            user.job = request_data['job']
        if 'birth_date' in request_data:
            user.birth_date = request_data['birth_date']

        # preferences
        preference = UserPreference.query.filter_by(user_id=user.id).first()
        print(preference)
        print(user)
        if not preference:
            print("creating preference")
            preference = UserPreference(user_id=user.id)
            db.session.add(preference)
            db.session.commit()
            print(preference.id)

        # passions
        user_passions = UserPassions.query.filter_by(user_id=user.id).all()
        if user_passions:
            for passion in user_passions:
                db.session.delete(passion)
            db.session.commit()
        if 'passions' in request_data:
            for passion_id in request_data['passions']:
                passion = UserPassions(user_id=user.id, passion_id=passion_id)
                db.session.add(passion)
                db.session.commit()
                print(passion_id)

        if 'age_min' in request_data:
            preference.age_min = request_data['age_min']
        if 'age_max' in request_data:
            preference.age_max = request_data['age_max']
        if 'interested_gender' in request_data:
            preference.interested_gender = request_data['interested_gender']
            print(request_data['interested_gender'])
        if 'sexual_orientation_id' in request_data:
            user.sexual_orientation_id = request_data['sexual_orientation_id']
        if 'long' in request_data:
            user.long = request_data['long']
        if 'lat' in request_data:
            user.lat = request_data['lat']
        if 'distance' in request_data:
            preference.distance = request_data['distance']
        if 'ytmusic_link' in request_data:
            user.ytmusic_link = request_data['gender']
        if 'spotify_link' in request_data:
            user.spotify_link = request_data['spotify_link']
            token = request_data['spotify_access_token']
            spotify = tk.Spotify(token)
            tracks = spotify.current_user_top_tracks(limit=50)
            for track in tracks.items:
                track_ids.append(track.id)
        db.session.add(user)
        db.session.commit()
        db.session.add(preference)
        db.session.commit()
        get_user_url = '/users/{0}'.format(user.public_id)
        user_details = requests.get(HRS_BASE_URL + get_user_url)
        if user_details.status_code == 200:
            try:
                res = requests.post(HRS_BASE_URL + '/users/', json={
                    "pref_age_min": preference.age_min,
                    "pref_age_max": preference.age_max,
                    "pref_interested_in": preference.interested_gender,
                    "pref_distance": preference.distance
                })
            except Exception as e:
                print(e)
        else:
            try:
                res = requests.post(HRS_BASE_URL + '/users/', json={
                    "id": user.public_id,
                    "pref_age_min": preference.age_min,
                    "pref_age_max": preference.age_max,
                    "gender": user.gender,
                    "pref_interested_in": preference.interested_gender,
                    "location": {
                        "long": user.long,
                        "lat": user.lat
                    },
                    "dob": user.birth_date.strftime("%Y-%m-%d"),
                    "tracks": track_ids,
                    "pref_distance": preference.distance
                })
            except Exception as e:
                print(e)
        return make_response(jsonify({'success': True}), 200)


class ProfileImages(Resource):

    @token_required
    def get(self, user):

        user_images = UserImages.query.filter_by(user_id=user.id).all()

        user_images_list = [{'ref': "", 'src': ""} for i in range(6)]

        for i in range(len(user_images)):
            user_images_list[i]['ref'] = user_images[i].img_ref
            user_images_list[i]['src'] = user_images[i].img_src

        return make_response(jsonify({'user_images': user_images_list}), 200)

    @token_required
    def post(self, user):

        request_data = request.get_json()

        if 'images' not in request_data:
            return make_response(jsonify({'msg': "images not uploaded properly"}), 404)

        user_images = UserImages.query.filter_by(user_id=user.id).all()
        if user_images:
            for img in user_images:
                db.session.delete(img)
            db.session.commit()

        user_images_list = []

        for img in request_data['images']:
            image = UserImages(user_id=user.id, img_ref=img["ref"], img_src=img["src"])
            user_images_list.append(image)

        db.session.add_all(user_images_list)
        db.session.commit()

        return make_response(jsonify({'img upload': 'successful'}), 200)


class UserProfileSuggestions(Resource):

    @token_required
    def get(self, user):
        request_data = request.args
        index = int(request_data['index'])
        offset = int(request_data['offset'])
        limit = index * offset
        recommendations = []
        get_recommendation_url = HRS_BASE_URL + "/users/{0}/recommend/".format(user.public_id)
        try:
            result = requests.get(get_recommendation_url, params={"lat": user.lat, "long": user.long, "limit": limit})
            if result.status_code == 200:
                recommendations = result.recommendations[(index - 1) * offset: limit]
        except Exception as e:
            print(e)
        if not recommendations:
            return make_response(jsonify(recommendations=recommendations), 200)
        recommended_data = []
        user_swipes = UserSwipes.query.filter_by(user_id=user.public_id).first()
        for recommendation in recommendations:
            if recommendation in user_swipes.swipe_ids:
                continue
            r_user = UserAccount.query.filter_by(public_id=recommendation).first()
            r_images = UserImages.query.filter_by(user_id=r_user.id).all()
            images = []
            for image in r_images:
                images.append({
                    'img_id': image.img_id,
                    'img_ref': image.img_ref,
                    'img_src': image.img_src
                })
            r_passions = UserPassions.query.filter_by(user_id=r_user.id).all()
            passions = []
            for r_passion in r_passions:
                passion = Passions.query.get(r_passion.passion_id)
                passions.append(passion.name)
            recommended_data.append({
                'public_id': r_user.public_id,
                'images': images,
                'age': (datetime.datetime.utcnow() - r_user.birth_date).year,
                'name': r_user.f_name,
                'passions': passions,
                'bio': r_user.bio,
                'job': r_user.job
            })
        return make_response(jsonify(recommendation=recommended_data), 200)


class UserSwipeUpdate(Resource):

    @token_required
    def post(self, user):
        request_data = request.get_json()
        user_swipes = UserSwipes.query.filter_by(user_id=user.public_id).first()
        right_swiped_users = request_data['right_swipe_ids']
        for user_id in right_swiped_users:
            swiped_user_swipe_list = UserSwipes.query.filter_by(user_id=user_id).first()
            if user.public_id in swiped_user_swipe_list.swipe_ids:
                notification12 = UserNotificationFeed(to_user_id=user.public_id,
                                                      from_user_id=user_id,
                                                      notification_type_id=1)
                notification21 = UserNotificationFeed(to_user_id=user_id,
                                                      from_user_id=user.public_id,
                                                      notification_type_id=1)
                match = UserMatches(
                    user_id_1=user_id,
                    user_id_2=user.public_id
                )
                db.session.add(match)
                db.session.add(notification12)
                db.session.add(notification21)
                db.session.commit()
            user_swipes.swipe_ids.append(user_id)
        db.session.add(user_swipes)
        db.session.commit()

        # Updating Recommendation Swipe List
        try:
            update_url = HRS_BASE_URL + '/users/{0}/update-right-swipes/'.format(user.public_id)
            response = requests.post(update_url, json={"swipees": right_swiped_users})
            print(response.json())
        except Exception as e:
            print(e)
        return make_response(jsonify(message="Successfully Uploaded Responses"), 200)


class NotificationFeed(Resource):

    @token_required
    def get(self, user):
        request_data = request.args
        notification_feed = UserNotificationFeed.query.filter_by(to_user_id=user.public_id).all()
        notifications = []
        for notification in notification_feed:
            if notification.created > request_data['last_feed_refresh_date']:
                new_notif = True
            else:
                new_notif = False
            from_user = UserAccount.query.filter_by(public_id=notification.from_user_id).first()
            notification_type = NotificationType.query.get(notification.notification_type_id)
            notifications.append({
                'from_name': from_user.f_name,
                'public_id': from_user.public_id,
                'messsage': notification_type.message,
                'new_notif': new_notif
            })
        return make_response(jsonify(notifications=notifications), 200)


class UserProfileView(Resource):

    @token_required
    def get(self, user):
        request_data = request.args
        print(request_data['user_id'])
        r_user = UserAccount.query.filter_by(public_id=request_data['user_id']).first()
        images = []
        r_images = UserImages.query.filter_by(user_id=r_user.id).all()
        for image in r_images:
            images.append({
                'img_id': image.img_id,
                'img_ref': image.img_ref,
                'img_src': image.img_src
            })
        r_passions = UserPassions.query.filter_by(user_id=r_user.id).all()
        passions = []
        for r_passion in r_passions:
            passion = Passions.query.get(r_passion.passion_id)
            passions.append(passion.name)
        user_data = {
            'public_id': r_user.public_id,
            'images': images,
            'age': (datetime.datetime.utcnow().year - r_user.birth_date.year),
            'name': r_user.f_name,
            'passions': passions,
            'bio': r_user.bio,
            'job': r_user.job
        }
        return make_response(jsonify(user_data=user_data), 200)


class UserMatches(Resource):

    @token_required
    def get(self, user):
        matches = UserMatches.query.filter(UserMatches.user_id_1 == user.public_id | UserMatches.user_id_2 == user.public_id).all()
        matches_data = []
        for match in matches:
            if match.user_id_1 == user.public_id:
                user_id = match.user_id_2
            else:
                user_id = match.user_id_1
            user_details = UserAccount.query.filter_by(public_id=user_id).first()
            matches_data.append({
                'match_id': match.id,
                'name': user_details.f_name,
                'public_id': user_details.public_id
            })
        return make_response(jsonify(matches=matches_data, success=True), 200)
