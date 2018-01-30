# Move tweets collected to S3 bucket
!aws s3 mv data/ s3://sgupta-s3/social_media/twitter/ --recursive