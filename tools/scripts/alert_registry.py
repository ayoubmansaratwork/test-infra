import re
from typing import Dict, Any, List, Union

import urllib
import os
from alert_utils import create_issue, clear_alerts, fetch_alerts_filter, REPO_OWNER, TEST_INFRA_REPO_NAME, GRAPHQL_URL, UPDATE_ISSUE_URL, ISSUES_WITH_LABEL_QUERY,CREATE_ISSUE_URL, PYTORCH_ALERT_LABEL, update_issue
import requests
import json
import pprint
ALERT_REGISTRY = {}

PENDING = "pending"
NEUTRAL = "neutral"
SKIPPED = "skipped"
SUCCESS = "success"
FAILURE = "failure"
CANCELED = "canceled"

# rename this when these are ready
# PYTORCH_ALERT_LABEL = "pytorch-alert"
PYTORCH_ALERT_LABEL = "pytorch-alert-test"

headers = {"Authorization": f"token {os.environ.get('GITHUB_TOKEN')}"}

def register_alert(alert_type):
    if alert_type in ALERT_REGISTRY:
        raise ValueError(f"Alert type {alert_type} is already registered")
    def inner(func):
        ALERT_REGISTRY[alert_type] = func
        return func
    return inner

def _assert_same_repo_and_type(alerts: List[Dict[str, Any]]) -> None:
    print(alerts[0])
    repo = alerts[0]["repo"]
    alert_type = alerts[0]["AlertType"]
    alert_org = alerts[0]["organization"]
    for alert in alerts:
        if alert["repo"] != repo:
            raise ValueError(
                f"Alerts must be from the same repository, got {repo} and {alert['repo']}"
            )
        if alert["AlertType"] != alert_type:
            raise ValueError(
                f"Alerts must be of the same type, got {alert_type} and {alert['AlertType']}"
            )
        if alert["organization"] != alert_org:
            raise ValueError(
                f"Alerts must be of the same org, got {alert_org} and {alert['org']}"
            )

@register_alert('Recurrently Failing Job')
def handle_recurrently_failing_jobs(alerts: List[Dict[str, Any]]) -> Any:
    _assert_same_repo_and_type(alerts)
    repo = alerts[0]["repo"]
    issue =  generate_failed_job_issue(alerts)
    existing_alerts = fetch_alerts_filter(repo, [PYTORCH_ALERT_LABEL], alerts[0]["AlertType"])
    clear_alerts(existing_alerts[:-1])
    if len(existing_alerts) == 0:
        existing_alerts.push(issue)
        create_issue(issue)
    else:
        update_issue(issue, existing_alerts[-1])
    return issue

def generate_failed_job_hud_link(failed_job_name: str) -> str:
    # TODO: I don't think minihud is universal across multiple repositories
    #       would be good to just replace this with something that is
    hud_link = "https://hud.pytorch.org/minihud?name_filter=" + urllib.parse.quote(
        failed_job_name
    )
    return f"[{failed_job_name}]({hud_link})"

def generate_failed_job_issue(
    alerts
) -> Any:
    alerts.sort(key=lambda alert: alert["AlertObject"])
    issue = {}
    issue[
        "title"
    ] = f"[{alerts[0]['repo']}] [{alerts[0]['AlertType']}] [TEST ALERT PAY NO ATTENTION TO THIS] There are {len(alerts)}"
    body = "Within the last 50 commits, there are the following failures on the main branch of pytorch: \n"
    closed_alerts = []
    for alert in alerts:
        if alert["closed"]:
            closed_alerts.append(job_name)
            continue
        job_name = alert["AlertObject"]
        body += (
            f"- {generate_failed_job_hud_link(job_name)} failed consecutively."
        )
        body += "\n\n"
    if len(closed_alerts) > 0:
        body += "These jobs stopped failing:\n"
        for job in closed_alerts:
            job_name = alert["AlertObject"]
            body += f"* {job_name}\n" 
        
        body += f"* {job_name}\n" 
    body += "Please review the errors and revert if needed."
    issue["body"] = body
    issue["labels"] = [PYTORCH_ALERT_LABEL]

    # print("Generating alerts for: ", alerts)
    return issue