import boto3

# 1.连接minio
s3 = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id="admin",
    aws_secret_access_key="admin123",
    region_name="us-east-1"
)

# 2. 创建 bucket
bucket_name = "test-bucket"
s3.create_bucket(Bucket=bucket_name)
print(f"Bucket '{bucket_name}' created.")

# 3. 上传对象
s3.put_object(Bucket=bucket_name, Key="hello.txt", Body=b"Hello MinIO!")
print("Uploaded hello.txt")

# 4. 列出对象
objects = s3.list_objects_v2(Bucket=bucket_name)
print("Objects in bucket:", [obj['Key'] for obj in objects.get('Contents', [])])

# 5. 下载对象
obj = s3.get_object(Bucket=bucket_name, Key="hello.txt")
content = obj['Body'].read().decode()
print("Downloaded content:", content)

# 6. 删除对象
s3.delete_object(Bucket=bucket_name, Key="hello.txt")
print("Deleted hello.txt")

# 7. 删除 bucket
s3.delete_bucket(Bucket=bucket_name)
print(f"Bucket '{bucket_name}' deleted.")