#!/bin/bash

# Project and VPC name
PROJECT_ID="ai-core-system-bot-prd"
VPC_NAME="ai-core-system-bot-prd-vpc"

# Get list of all regions with subnets for this VPC
REGIONS=$(gcloud compute networks subnets list --project=$PROJECT_ID --network=$VPC_NAME --format="value(region.basename())")

# Delete each subnet in each region
for REGION in $REGIONS; do
  echo "Deleting subnet in region: $REGION"
  gcloud compute networks subnets delete $VPC_NAME --project=$PROJECT_ID --region=$REGION --quiet
done

echo "All subnets deleted. Now trying to delete the VPC network..."
gcloud compute networks delete $VPC_NAME --project=$PROJECT_ID --quiet

