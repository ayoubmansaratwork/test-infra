import re
from typing import Dict, Any, List, Union

import urllib

from check_alerts import FAILED_JOB_PATTERN, PYTORCH_ALERT_LABEL, JobStatus, generate_failed_job_hud_link

ALERT_REGISTRY = {}

PENDING = "pending"
NEUTRAL = "neutral"
SKIPPED = "skipped"
SUCCESS = "success"
FAILURE = "failure"
CANCELED = "canceled"
PYTORCH_ALERT_LABEL = "pytorch-alert"

def register_alert(alert_type):
    if alert_type in ALERT_REGISTRY:
        raise ValueError(f"Alert type {alert_type} is already registered")
    def inner(func):
        ALERT_REGISTRY[alert_type] = func
        return func
    return inner

@register_alert('Recurrently Failing Job')
def handle_recurrently_failing_jobs(alerts: List[Dict[str, Any]]) -> Any:
    return generate_failed_job_issue(alerts)

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
    ] = f"[Pytorch] There are {len(alerts)}"
    body = "Within the last 50 commits, there are the following failures on the main branch of pytorch: \n"
    closed_alerts = []
    for alert in alerts:
        if alert["closed"]:
            closed_alerts.append(job_name)
            continue
        job_name = alert["AlertObject"]
        oncalls = alert["OncallTeams"]
        individuals = alert["OncallIndividuals"]
        body += (
            f"- {generate_failed_job_hud_link(job_name)} failed consecutively. Oncalls: {oncalls}. Individuals: {individuals}"
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

    print("Generating alerts for: ", alerts)
    return issue