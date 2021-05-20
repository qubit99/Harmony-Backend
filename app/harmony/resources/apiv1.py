from flask_restful import Resource
from flask import Flask, request, jsonify, make_response

from harmony.models.user import UserAccount, UserPreference, SexualOrientation, Passions, UserPassions, UserImages
from harmony.resources.auth import token_required
from harmony import db


class UserSettings(Resource):
    # method_decorators = [token_required]

    @token_required
    def get(self, user):
        request_data = request.args
        
        preference = UserPreference.query.filter_by(user_id = user.id).first()
        
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

        #passions
        passion_list = Passions.query.all()
        passions = [{'passion_id':passion.id, 'passion_name':passion.name} for passion in Passions.query.all()]
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
            'passion_list':passions,
            'user_passions':User_passions,
            'ytmusic_link': user.ytmusic_link,
            'spotify_link': user.spotify_link
        }
        return make_response(jsonify({'success': True, 'data': data}), 200)

    @token_required
    def post(self, user):

        request_data = request.get_json()
        
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
        
        #preferences
        preference = UserPreference.query.filter_by(user_id=user.id).first()
        print(preference)
        print(user)
        if not preference:
            print("creating preference")
            preference = UserPreference(user_id=user.id)
            db.session.add(preference)
            db.session.commit()
            print(preference.id)
            
        

        #passions
        user_passions = UserPassions.query.filter_by(user_id=user.id).all()
        if user_passions:
            for passion in user_passions:
                db.session.delete(passion)
            db.session.commit()
        if 'passions' in request_data:
            for passion_id in request_data['passions']:
                passion = UserPassions(user_id = user.id, passion_id = passion_id)
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
        if 'ytmusic_link' in request_data:
            user.ytmusic_link = request_data['gender']
        if 'spotify_link' in request_data:
            user.spotify_link = request_data['spotify_link']
        db.session.add(user)
        db.session.commit()
        db.session.add(preference)
        db.session.commit()
        
        return make_response(jsonify({'success': True}), 200)

class ProfileImages(Resource):

    @token_required
    def get(self, user):

        user_images = UserImages.query.filter_by(user_id = user.id).all()
        
        user_images_list = [{'ref':None, 'src':""} for i in range(6)]

        for i in range(len(user_images)):
            user_images_list[i]['ref'] = user_images[i].img_ref
            user_images_list[i]['src'] = user_images[i].img_src

        return make_response(jsonify({'user_images':user_images_list}), 200)

    @token_required
    def post(self, user):

        request_data = request.get_json()
        
        if 'images' not in request_data:
            return make_response(jsonify({'msg':"images not uploaded properly"}), 404)
        
        user_images = UserImages.query.filter_by(user_id=user.id).all()
        if user_images:
            for img in user_images:
                db.session.delete(img)
            db.session.commit()

        user_images_list=[]
        
        for img in request_data['images']:

            image = UserImages(user_id = user.id, img_ref = img["ref"], img_src = img["src"])
            user_images_list.append(image)
        
        db.session.add_all(user_images_list)
        db.session.commit()

        return make_response(jsonify({'img upload': 'successful'}), 200)


        


