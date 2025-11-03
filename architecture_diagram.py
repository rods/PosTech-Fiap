from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda, ECS
from diagrams.aws.database import Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.network import ALB, CloudFront
from diagrams.aws.integration import Eventbridge
from diagrams.aws.management import Cloudwatch

with Diagram("Books Scraper Architecture", show=False, direction="LR"):
    
    cloudwatch = Cloudwatch("CloudWatch\nLogs & Metrics")
    
    with Cluster("CDN"):
        cdn = CloudFront("CloudFront\nDistribution")
    
    with Cluster("Data Collection"):
        scraper = Lambda("Web Scraper\nLambda")
        s3 = S3("CSV Storage\nS3 Bucket")
        
    with Cluster("Data Processing"):
        eventbridge = Eventbridge("S3 Event\nTrigger")
        loader = Lambda("CSV Loader\nLambda")
        
    with Cluster("Data Storage"):
        dynamodb = Dynamodb("Books\nDynamoDB")
        
    with Cluster("API Layer"):
        alb = ALB("Application\nLoad Balancer")
        ecs = ECS("FastAPI\nECS Fargate")
    
    # Flow
    scraper >> Edge(label="upload CSV") >> s3
    s3 >> Edge(label="trigger") >> eventbridge
    eventbridge >> Edge(label="invoke") >> loader
    loader >> Edge(label="write") >> dynamodb
    cdn >> Edge(label="route") >> alb
    alb >> Edge(label="forward") >> ecs
    ecs >> Edge(label="read/write") >> dynamodb
    
    # Logging
    scraper >> Edge(label="logs", style="dashed") >> cloudwatch
    loader >> Edge(label="logs", style="dashed") >> cloudwatch
    ecs >> Edge(label="logs", style="dashed") >> cloudwatch
