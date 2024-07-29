from flask import Flask, render_template, request
import os, json, boto3
from botocore.config import Config as s3Config
import logging
import random
import string
import requests

S3_BUCKET = os.environ.get('S3_BUCKET', '')
MAX_SIZE = int(os.environ.get("MAX_SIZE", 20)) 
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
PORT = int(os.environ.get('PORT', 5000))
POST_LMBDA_URL = os.environ.get('POST_LMBDA_URL', '')

gunicorn_logger = logging.getLogger('gunicorn.error')

s3_config = s3Config(
	region_name = os.environ.get('S3_REGION', 'us-east-2'),
	signature_version = 'v4',
 	retries = {
		'max_attempts': 5,
		'mode': 'standard'
	}
)


def create_app() -> Flask:

	app = Flask(__name__)

	@app.route("/")
	def main():
		return render_template('index.html')

	@app.route('/v2/sign-s3/')
	def sign_s3_v2():
		request_dict = {
			"fileName": request.args.get('fileName'),
			"fileType": request.args.get('fileType'),
			"t": int(request.args.get('t'))
		}
		api_url = f"https://{POST_LMBDA_URL}/sign-s3?fileName={request_dict['fileName']}&fileType={request_dict['fileType']}&t={request_dict['t']}"
		ret_val = requests.get(api_url).json()
		return ret_val
	
	#Fallback
	@app.route('/v1/sign-s3/')
	def sign_s3():
		return {'error':'INVALID API URL'}
		# left here as backup
		file_name = request.args.get('fileName')
		file_type = request.args.get('fileType')
		file_size = int(request.args.get('t'))

		return_data = {
			'data':'',
			'url':'',
			'error':''
		}
		s3 = boto3.client('s3', config=s3_config)
		# Check file does not exist. It really shouldnt with a 16 length random string prefix but you never know...
		while True:
			prefix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
			filenamefull = f'{prefix}/{file_name}'
			try:
				s3.head_object(Bucket = S3_BUCKET, Key = filenamefull)
			except:
				break
		#TODO: make this a conditional with the generated presigned post url? content-length-range maybe?
		if file_size >= MAX_SIZE * 1024 * 1024:
			return_data['error'] = f"The requested file size was too large! The max size is {MAX_SIZE} MB"
		
		elif "image/" not in file_type:
			return_data['error'] = "The requested type was not an image!"
   
		elif S3_BUCKET == '':
			return_data['error'] = "The specified target for the file upload does not exist!"
   
		if return_data['error'] == '':  
				
			try:
				return_data['data'] = s3.generate_presigned_post(
					Bucket = S3_BUCKET,
					Key = filenamefull,
					Fields = {"Content-Type": file_type},
					Conditions = [
						{ "Content-Type": file_type }
					],
					ExpiresIn = 3600
				)

				return_data['url'] = f'https://{S3_BUCKET}/{prefix}/{file_name}'

			except TypeError as e:
				return_data['error'] = 'Failed to authenticate file'
				gunicorn_logger.error("Upload error: %s", return_data['error'])
		else:
			gunicorn_logger.error("Upload error: %s", return_data['error'])
   

		return json.dumps(return_data)

	return app

if __name__ == '__main__':
    # For debugging. Just run the script raw without gunicorn
	create_app().run(
     	host='0.0.0.0', 
		port = PORT, 
		debug=True)