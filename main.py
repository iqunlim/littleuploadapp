from flask import Flask, render_template, request
import os, json, boto3

S3_BUCKET = os.environ.get('S3_BUCKET', 'test0bucket-234234')
MAX_SIZE = int(os.environ.get("MAX_SIZE", 20)) 
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
PORT = int(os.environ.get('PORT', 5000))

def create_app() -> Flask:

	app = Flask(__name__)


	@app.route("/")
	def main():
		return render_template('upload.html')

	'''
 	@app.route("/target")
	def boop():
		return "Hello"
	'''

	@app.route('/sign-s3/')
	def sign_s3():

		file_name = request.args.get('fileName')
		file_type = request.args.get('fileType')
		file_size = int(request.args.get('t'))

		return_data = {
			'data':'',
			'url':'',
			'error':''
		}

		if file_size >= MAX_SIZE * 1024 * 1024:
			return_data['error'] = f"The requested file size was too large! The max size is {MAX_SIZE} MB"

		if "image/" not in file_type:
			return_data['error'] = "The requested type was not an image!"

		if return_data['error'] == '':  
			s3 = boto3.client('s3')
			try:
				return_data['data'] = s3.generate_presigned_post(
					Bucket = S3_BUCKET,
					Key = file_name,
					Fields = {"Content-Type": file_type},
					Conditions = [
						{ "Content-Type": file_type }
					],
					ExpiresIn = 3600
				)

				return_data['url'] = f'https://{S3_BUCKET}.s3.amazonaws.com/{file_name}'

			except TypeError:
				return_data['error'] = 'Failed to authenticate file'

		return json.dumps(return_data)

	return app

if __name__ == '__main__':
    # For debugging. Just run the script raw without gunicorn
	create_app().run(
     	host='0.0.0.0', 
		port = PORT, 
		debug=True)