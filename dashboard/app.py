import streamlit as st
import boto3
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="API Dashboard", layout="wide")
st.title("Books API Monitoring Dashboard")

# AWS region
AWS_REGION = st.secrets.get("AWS_REGION", "us-east-2")

# AWS clients
session = boto3.Session(
    aws_access_key_id=st.secrets.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=st.secrets.get("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION
)
cloudwatch = session.client('cloudwatch')
logs = session.client('logs')
# CloudFront metrics are only in us-east-1
cloudwatch_us_east_1 = session.client('cloudwatch', region_name='us-east-1')

# Time range selector
col1, col2 = st.columns(2)
with col1:
    hours = st.selectbox("Time Range", [1, 6, 12, 24], index=1)
with col2:
    if st.button("Refresh"):
        st.rerun()

end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=hours)

# ECS Metrics
st.header("ECS Service")
col1, col2, col3 = st.columns(3)

def get_metric(namespace, metric_name, dimensions, stat='Average'):
    response = cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=[stat]
    )
    return response['Datapoints']

def get_metric_cf(namespace, metric_name, dimensions, stat='Average'):
    response = cloudwatch_us_east_1.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=[stat]
    )
    return response['Datapoints']

# Load from secrets or use text input as fallback
CLUSTER_NAME = st.secrets.get("CLUSTER_NAME", st.text_input("ECS Cluster Name", ""))
SERVICE_NAME = st.secrets.get("SERVICE_NAME", st.text_input("ECS Service Name", ""))
ALB_NAME = st.secrets.get("ALB_NAME", st.text_input("ALB Name", ""))
DISTRIBUTION_ID = st.secrets.get("DISTRIBUTION_ID", st.text_input("CloudFront Distribution ID", ""))

if CLUSTER_NAME and SERVICE_NAME:
    ecs_dims = [
        {'Name': 'ClusterName', 'Value': CLUSTER_NAME},
        {'Name': 'ServiceName', 'Value': SERVICE_NAME}
    ]
    
    cpu = get_metric('AWS/ECS', 'CPUUtilization', ecs_dims)
    memory = get_metric('AWS/ECS', 'MemoryUtilization', ecs_dims)
    
    with col1:
        st.metric("Avg CPU", f"{cpu[-1]['Average']:.1f}%" if cpu else "N/A")
    with col2:
        st.metric("Avg Memory", f"{memory[-1]['Average']:.1f}%" if memory else "N/A")
    with col3:
        tasks = get_metric('ECS/ContainerInsights', 'RunningTaskCount', 
                          [{'Name': 'ClusterName', 'Value': CLUSTER_NAME}], 'Average')
        st.metric("Running Tasks", f"{int(tasks[-1]['Average'])}" if tasks else "N/A")

# ALB Metrics
st.header("Load Balancer")
col1, col2, col3 = st.columns(3)

if ALB_NAME:
    alb_dims = [{'Name': 'LoadBalancer', 'Value': ALB_NAME}]
    
    requests = get_metric('AWS/ApplicationELB', 'RequestCount', alb_dims, 'Sum')
    latency = get_metric('AWS/ApplicationELB', 'TargetResponseTime', alb_dims, 'Average')
    errors = get_metric('AWS/ApplicationELB', 'HTTPCode_Target_5XX_Count', alb_dims, 'Sum')
    
    with col1:
        st.metric("Total Requests", f"{sum([d['Sum'] for d in requests]):.0f}" if requests else "0")
    with col2:
        st.metric("Avg Latency", f"{latency[-1]['Average']:.3f}s" if latency else "N/A")
    with col3:
        st.metric("5XX Errors", f"{sum([d['Sum'] for d in errors]):.0f}" if errors else "0")
    
    # Latency chart
    if latency:
        df = pd.DataFrame(latency)
        df = df.sort_values('Timestamp')
        st.line_chart(df.set_index('Timestamp')['Average'])

# CloudFront Metrics
st.header("CloudFront")
col1, col2, col3 = st.columns(3)

if DISTRIBUTION_ID:
    cf_dims = [{'Name': 'DistributionId', 'Value': DISTRIBUTION_ID}, {'Name': 'Region', 'Value': 'Global'}]
    
    cf_requests = get_metric_cf('AWS/CloudFront', 'Requests', cf_dims, 'Sum')
    cache_hit = get_metric_cf('AWS/CloudFront', 'CacheHitRate', cf_dims, 'Average')
    cf_errors = get_metric_cf('AWS/CloudFront', '5xxErrorRate', cf_dims, 'Average')
    
    with col1:
        st.metric("Total Requests", f"{sum([d['Sum'] for d in cf_requests]):.0f}" if cf_requests else "0")
    with col2:
        st.metric("Cache Hit Rate", f"{cache_hit[-1]['Average']:.1f}%" if cache_hit else "N/A")
    with col3:
        st.metric("5XX Error Rate", f"{cf_errors[-1]['Average']:.2f}%" if cf_errors else "0%")

# CloudWatch Logs Insights
st.header("API Logs")
LOG_GROUP = st.secrets.get("LOG_GROUP", st.text_input("Log Group Name", ""))

if LOG_GROUP and st.button("Query Logs"):
    query = """
    fields @timestamp, @message
    | limit 100
    """
    
    response = logs.start_query(
        logGroupName=LOG_GROUP,
        startTime=int(start_time.timestamp()),
        endTime=int(end_time.timestamp()),
        queryString=query
    )
    
    query_id = response['queryId']
    
    # Wait for query
    import time
    result = None
    for _ in range(30):
        result = logs.get_query_results(queryId=query_id)
        if result['status'] == 'Complete':
            break
        time.sleep(1)
    
    if result and result['results']:
        data = []
        for row in result['results']:
            data.append({field['field']: field['value'] for field in row})
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No logs found or query timed out")
