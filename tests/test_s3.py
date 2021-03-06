import botocore
import pytest

from notifications_utils.s3 import s3upload

contents = 'some file data'
region = 'eu-west-1'
bucket = 'some_bucket'
location = 'some_file_location'


def test_s3upload_save_file_to_bucket(mocker):
    mocked = mocker.patch('notifications_utils.s3.resource')
    s3upload(filedata=contents,
             region=region,
             bucket_name=bucket,
             file_location=location)
    mocked_put = mocked.return_value.Object.return_value.put
    mocked_put.assert_called_once_with(Body=contents, ServerSideEncryption='AES256')


def test_s3upload_creates_bucket_if_bucket_does_not_exist(mocker):
    mocked = mocker.patch('notifications_utils.s3.resource')
    response = {'Error': {'Code': 404}}
    exception = botocore.exceptions.ClientError(response, 'Does not exist')
    mocked.return_value.meta.client.head_bucket.side_effect = exception
    s3upload(filedata=contents,
             region=region,
             bucket_name=bucket,
             file_location=location)
    mocked_create_bucket = mocked.return_value.create_bucket
    mocked_create_bucket.assert_called_once_with(Bucket=bucket,
                                                 CreateBucketConfiguration={'LocationConstraint': region})


def test_s3upload_raises_exception(app, mocker):
    mocked = mocker.patch('notifications_utils.s3.resource')
    response = {'Error': {'Code': 500}}
    exception = botocore.exceptions.ClientError(response, 'Bad exception')
    mocked.return_value.meta.client.head_bucket.side_effect = exception
    with pytest.raises(botocore.exceptions.ClientError):
        s3upload(filedata=contents,
                 region=region,
                 bucket_name=bucket,
                 file_location="location")
