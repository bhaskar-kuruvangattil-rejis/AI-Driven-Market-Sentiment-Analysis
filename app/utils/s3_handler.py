import boto3
import os
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3Handler:
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is not set")
        
        try:
            self.s3_client = boto3.client(
                "s3",
                region_name=self.aws_region
            )
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure AWS credentials.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    def save_raw_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save raw text to S3 with optional metadata"""
        try:
            timestamp = datetime.now().isoformat()
            filename = f"raw/text/{timestamp}.txt"
            
            # Prepare metadata
            s3_metadata = {
                "timestamp": timestamp,
                "content_type": "text/plain",
                "source": "sentiment_analysis_app"
            }
            if metadata:
                s3_metadata.update(metadata)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=text.encode('utf-8'),
                Metadata={k: str(v) for k, v in s3_metadata.items()},
                ContentType="text/plain"
            )
            
            logger.info(f"Successfully saved raw text to S3: {filename}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to save text to S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving to S3: {e}")
            return False
    
    def save_analysis_result(self, text: str, sentiment: str, confidence: float) -> bool:
        """Save sentiment analysis result as JSON to S3"""
        try:
            timestamp = datetime.now().isoformat()
            filename = f"processed/sentiment/{timestamp}.json"
            
            analysis_data = {
                "timestamp": timestamp,
                "text": text,
                "sentiment": sentiment,
                "confidence": confidence,
                "processed_by": "aws_comprehend"
            }
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=json.dumps(analysis_data, indent=2).encode('utf-8'),
                ContentType="application/json",
                Metadata={
                    "timestamp": timestamp,
                    "sentiment": sentiment,
                    "confidence": str(confidence)
                }
            )
            
            logger.info(f"Successfully saved analysis result to S3: {filename}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to save analysis result to S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving analysis result to S3: {e}")
            return False
    
    def list_objects(self, prefix: str = "", limit: int = 10) -> list:
        """List objects in S3 bucket with optional prefix"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            if 'Contents' in response:
                objects = [{
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                } for obj in response['Contents']]
                logger.info(f"Listed {len(objects)} objects from S3")
                return objects
            else:
                logger.info("No objects found in S3 bucket")
                return []
                
        except ClientError as e:
            logger.error(f"Failed to list S3 objects: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing S3 objects: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test S3 connection by attempting to list bucket contents"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info("S3 connection test successful")
            return True
        except ClientError as e:
            logger.error(f"S3 connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error testing S3 connection: {e}")
            return False


# Global S3 handler instance
s3_handler = S3Handler()


def save_to_s3(text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Legacy function for backward compatibility"""
    return s3_handler.save_raw_text(text, metadata)
