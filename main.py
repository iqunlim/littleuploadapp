from flask import Flask, render_template, request
import os, json, boto3
import logging.config


S3_BUCKET = os.environ.get('S3_BUCKET')
MAX_SIZE = int(os.environ.get("MAX_SIZE", 20)) 
CUR_DIR = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(CUR_DIR + '/logs'):
  os.makedirs(CUR_DIR + '/logs')

app = Flask(__name__)
logger = logging.getLogger(__name__)

with open(CUR_DIR + '/static/config/logging.json') as config_in:
      logging_config = json.load(config_in)
      logging.config.dictConfig(config=logging_config)
      

@app.route("/")
def main():
    return render_template('upload.html')
  
'''@app.route("/target")
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
          {
            "Content-Type": file_type
          }
        ],
        ExpiresIn = 3600
      )
      
      return_data['url'] = f'https://{S3_BUCKET}.s3.amazonaws.com/{file_name}'
      
    except TypeError:
      return_data['error'] = 'Failed to authenticate file'
    
  return json.dumps(return_data)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port = port, debug=True)