#!/usr/bin/env python3

import argparse
import boto3
import datetime
import logging

# Create EC2 client
ec2 = boto3.client("ec2")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Terminate orphaned bluesky-aws AWS EC2 instances.")
    parser.add_argument("--hours", type=float, required=True,
        help=("Minimum age, in hours, of instances to be stopped."
            " Can be fractional - e.g. 0.25"))
    parser.add_argument("-n", "--name-pattern", type=str, required=True,
        help="Instance name pattern to filter (optional)")
    parser.add_argument("--terminate", action="store_true",
        help="Terminate instances instead of just stopping")
    parser.add_argument("--log-level", type=str, default="INFO",
        help="Log level - DEBUG, INFO, etc.")
    parser.add_argument("-d", "--dry-run", action="store_true",
        help="Dry run - don't terminate instances")

    return parser.parse_args()


def get_orphaned_instances(args):
    filters = [{"Name": "instance-state-name", "Values": ["running"]}]

    if args.name_pattern:
        filters.append({"Name": "tag:Name", "Values": [f"*{args.name_pattern}*"]})  # Wildcard search

    response = ec2.describe_instances(Filters=filters)

    instances_to_terminate = []

    now = datetime.datetime.now(datetime.UTC)

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            launch_time = instance["LaunchTime"]
            runtime = now - launch_time

            if runtime.total_seconds() > args.hours * 3600:
                instance_id = instance["InstanceId"]
                instance_name = next(
                    (tag["Value"] for tag in instance.get("Tags", [])
                        if tag["Key"] == "Name"), "Unnamed"
                )

                instances_to_terminate.append({
                    'id': instance_id,
                    'name':instance_name,
                    'runtime': runtime
                })

    return instances_to_terminate

def stop_instances(args, instances):
    """Terminate the specified EC2 instances."""
    if instances:
        logging.info('Instances to terminate:')
        for i in instances:
            logging.info(f"  {i['id']}  -  {i['name']}  - {i['runtime'].total_seconds() / 3600}")

        instance_ids = [i['id'] for i in instances]
        if args.dry_run:
            logging.info(f"[DRY RUN] Instances that would be {'terminated' if args.terminate else 'stopped'}: {instance_ids}")
        else:
            if args.terminate:
                logging.info(f"Terminating instance instances: {instance_ids}")
                ec2.terminate_instances(InstanceIds=instance_ids)
            else:
                logging.info(f"Stoppinng instance instances: {instance_ids}")
                ec2.stop_instances(InstanceIds=instance_ids)
    else:
        logging.info("No instances found that need to be terminated.")

if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s')

    instances = get_orphaned_instances(args)

    if instances:
        stop_instances(args, instances)
    else:
        logging.info("No matching instances found.")
