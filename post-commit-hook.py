#!/usr/bin/env python   1
# --*-- encoding: iso-8859-1 --*--

import subprocess
import re
# jira python library - https://jira.readthedocs.io/en/master/index.html
from jira import JIRA

# Jira settings
JIRA_URL = "https://JIRA_NAME.atlassian.net"
JIRA_USERNAME = "USER_NAME"
# For Jira Cloud use a token generated here: https://id.atlassian.com/manage/api-tokens
JIRA_API_TOKEN = ""

# This Regex looks for text in the form of JIRA-PROJECT_CODE-TICKET_NO
REGEX_ISSUE_ID = "JIRA\-([a-zA-Z]*)\-([0-9]*)"
# Seperator between the ISSUE_ID and commit message
ID_COMMIT_SEPERATOR = "-"


def execute_cmd(full_cmd, cwd=None):
    """Execute a git command"""
    process = subprocess.Popen(
        full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=cwd)
    (stdoutdata, stderrdata) = process.communicate(None)
    if 0 != process.wait():
        raise Exception("Could not execute git command")

    return (stdoutdata.strip(), stderrdata.strip())


def get_last_commit_message():
    """Get the message of the last committed commit"""
    return execute_cmd("git show -s --format=%s")[0]


def check_for_jira_commit(comment):
    """Check for Jira specific format of commit message"""
    jira_id = re.search(REGEX_ISSUE_ID, comment)
    if(jira_id):
        return True
    else:
        return False


def add_jira_comment(comment):
    """Adds a jira comment to the desired ticket"""
    # a username/password tuple
    jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
    has_jira_commit = check_for_jira_commit(comment)
    if has_jira_commit:
        jira_id = re.search(REGEX_ISSUE_ID, comment)
        prefix_length = len(jira_id[0] + ID_COMMIT_SEPERATOR)
        message = comment[prefix_length:]
        ticket_code = extract_ticket_code(jira_id)
        jira.add_comment(ticket_code, message)


def extract_ticket_code(jira_id):
    """Extract ticket code from commit message prefix"""
    split_jira_id = jira_id[0].split('-')
    ticket_code = split_jira_id[1] + '-' + split_jira_id[2]
    return ticket_code


commit_message = get_last_commit_message()
add_jira_comment(commit_message)
