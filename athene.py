#!/usr/bin/env python3

# AtheneCLI version 0.3

import getpass
import sys
import time
import requests
import html
import re
import json
import argparse

from pathlib import Path
from typing import NamedTuple

def parse_arguments():
	assignment_options = argparse.ArgumentParser(add_help=False)
	# assignment_options.add_argument("-i", "--id",
	# 	help="Athene assignment id.")
	
	root_parser = argparse.ArgumentParser()
	subparsers = root_parser.add_subparsers(dest="subcommand", required=True)
	
	submit_parser = subparsers.add_parser("submit", parents=[assignment_options],
		help="Sumbits files to an Athene assignment.")
	submit_parser.add_argument("files",
		help="Files to submit, in the order that they appear on the Athene page.",
		type=Path, nargs='*')
	
	subparsers.add_parser("status", parents=[assignment_options],
		help="Fetches the status of an Athene assignment.")
	
	subparsers.add_parser("clear", parents=[],
		help="Clears cached Athene information for the current directory.")
	
	return root_parser.parse_args()

def main():
	args = parse_arguments()
	
	with requests.Session() as http:
		if args.subcommand == "submit":
			subcommand_submit(args, http)
		elif args.subcommand == "status":
			subcommand_status(args, http)
		elif args.subcommand == "clear":
			subcommand_clear()

TERM_RESET = "\033[0m"
TERM_BOLD = "\033[1m"
TERM_RED = "\033[31m"
TERM_GREEN = "\033[32m"
TERM_INVERT = "\033[7m"

def subcommand_submit(args, http: requests.Session):
	initial_res = load_initial_response(http)
	athene_res = initial_res.athene_res
	
	print()
	
	if athene_res.pending:
		print("Submission is still being graded.")
		return
	
	if len(args.files) != len(athene_res.file_upload_slots):
		slot_names = ", ".join(slot.name for slot in athene_res.file_upload_slots)
		
		print(f"Incorrect number of files to submit. Expected {len(athene_res.file_upload_slots)} file(s): {slot_names}.")
		return
	
	files = {slot.id: (path.name, path.read_bytes()) for slot, path in zip(athene_res.file_upload_slots, args.files, strict=True)}
	submit_res = http.post(initial_res.assignment_url, files=files)
	
	if submit_res.status_code >= 400:
		raise Exception(f"Unknown issue submitting files, session may have expired. Status code: {submit_res.status_code}, Response: {submit_res.text}")
	
	print(TERM_BOLD + "Submitted files" + TERM_RESET)
	
	start_time = time.monotonic()
	last_time = start_time
	
	while True:
		print(f"\rWaiting for Athene to grade submission... {format_duration(int(time.monotonic() - start_time))} ", end="", flush=True)
		
		time.sleep(1)
		
		cur_time = time.monotonic()
		
		if cur_time - last_time >= 2:
			last_time = cur_time
			athene_res = send_athene_request(http, initial_res.assignment_url)
			
			if athene_res.session_timeout:
				print()
				print(TERM_BOLD + "Session timeout, use \"athene.py status\" to check status." + TERM_RESET)
				return
			
			if not athene_res.pending: break
	
	print()
	print()
	
	if athene_res.results is None:
		raise Exception("Submission is not pending, but no results found")
	
	print_submission_results(athene_res.results)

def subcommand_status(args, http: requests.Session):
	athene_res = load_initial_response(http).athene_res
	
	if athene_res.pending:
		print("Submission is still being graded.")
	elif athene_res.results is not None:
		print()
		print_submission_results(athene_res.results)
	else:
		print("No submissions yet.")

def subcommand_clear():
	local_config_path().unlink(missing_ok=True)

class CodeBlock(NamedTuple):
	title: str
	content: str

class UploadSlot(NamedTuple):
	id: str
	name: str

class SubmitResults(NamedTuple):
	test_cases_passed: int
	total_test_cases: int
	
	code_blocks: list[CodeBlock]
	
	points: int | None = None
	total_points: int | None = None

class AtheneResponse(NamedTuple):
	session_timeout: bool = False
	pending: bool = False
	
	results: SubmitResults | None = None
	file_upload_slots: list[UploadSlot] | None = None

class InitialResponse(NamedTuple):
	athene_res: AtheneResponse
	assignment_id: str
	assignment_url: str

def load_initial_response(http: requests.Session) -> InitialResponse:
	local_config = load_local_config()
	
	if local_config is None:
		assignment_id = input_assignment_id()
		auth_token = input_auth_token()
	else:
		assignment_id = local_config.assignment_id
		auth_token = local_config.auth_token
	
	assignment_url = f"https://athenecurricula.org/problem/{assignment_id}/"
	
	http.cookies.set("PHPSESSID", auth_token, domain="athenecurricula.org")
	
	athene_res = send_athene_request(http, assignment_url)
	
	if athene_res.session_timeout:
		if local_config is None:
			print("Either session timed out or invalid session token/assignment ID")
			sys.exit(0)
		else:
			print("Session timeout")
			
			auth_token = input_auth_token()
						
			http.cookies.set("PHPSESSID", auth_token, domain="athenecurricula.org")
			athene_res = send_athene_request(http, assignment_url)
			
			if athene_res.session_timeout:
				print("Repeated athene session timeout")
				sys.exit(0)
	
	local_config = LocalConfig(
		assignment_id=assignment_id,
		auth_token=auth_token
	)
	
	write_local_config(local_config)
	
	return InitialResponse(athene_res, assignment_id, assignment_url)

def input_assignment_id() -> str:
	# print("The assignment id can be taken from the URL of the Athene page.")
	# print("You won't have to enter the id again for this directory.")
	assign_id = input(TERM_BOLD + "Enter Assignment ID: " + TERM_RESET).strip()
	# print()
	
	if not assign_id:
		sys.exit(0)
	
	return assign_id

def input_auth_token() -> str:
	# print("Your Athene token can be gotten by using your browser's dev tools to")
	# print("find the PHPSESSID cookie on the Athene page.")
	# print("You won't have to enter the token again for this directory unless it expires.")
	auth_token = getpass.getpass(TERM_BOLD + "Enter Athene Token (not echoed): " + TERM_RESET)
	# print()
	
	if not auth_token:
		sys.exit(0)
	
	return auth_token

def print_submission_results(results: SubmitResults):
	test_cases_color = TERM_RED if results.test_cases_passed < results.total_test_cases else TERM_GREEN
	
	print(test_cases_color + TERM_BOLD + f"Passed {results.test_cases_passed} of {results.total_test_cases} test cases" + TERM_RESET)
	
	if results.points is not None and results.total_points is not None:
		print(f"Received {results.points} out of {results.total_points} points")
	
	print()
	
	for code_block in results.code_blocks:
		print(TERM_BOLD + code_block.title + TERM_RESET)
		print(code_block.content)

def send_athene_request(http: requests.Session, assignment_url: str, **kargs) -> AtheneResponse:
	res = http.get(assignment_url, **kargs)
	
	return parse_athene_response(res.text)

def format_duration(secs: int) -> str:
	if secs < 60:
		return f"{secs}s"
	else:
		return f"{secs // 60}m {secs % 60}s"

class LocalConfig(NamedTuple):
	assignment_id: str
	auth_token: str

def local_config_path() -> Path:
	return Path.cwd() / ".athene"

def load_local_config() -> LocalConfig | None:
	config_path = local_config_path()
	
	if not config_path.exists(): return None
	
	config_json = json.loads(config_path.read_text())
	
	return LocalConfig(
		assignment_id=config_json["assignment_id"],
		auth_token=config_json["auth_token"],
	)

def write_local_config(config: LocalConfig):
	config_json = {
		"assignment_id": config.assignment_id,
		"auth_token": config.auth_token,
	}
	
	config_path = local_config_path()
	
	config_path.write_text(json.dumps(config_json))
	config_path.chmod(0o600); # Read & write for owner only

SCORE_REGEX = re.compile(r"Score: (\d+)/(\d+) points")
TEST_CASES_REGEX = re.compile(r"You passed (\d+) of (\d+) test cases.")

CODE_BLOCK_REGEX = re.compile(r"<b>([^<]+)</b>\s*<pre class=(\w+)>\s*<span>([^<]*)</span>\s*</pre>")
FILE_UPLOAD_REGEX = re.compile(r"<tr><th align=right>([^<]*)</th><td><input size=\d+ type=file name=(file\d+)></td></tr>")

def parse_athene_response(html_text: str) -> AtheneResponse:
	if "Your session has timed out. Please refresh the page." in html_text:
		return AtheneResponse(session_timeout=True)
	
	if "... pending ..." in html_text:
		return AtheneResponse(pending=True)
	
	results = None
	
	if (results_start := html_text.find("Most recent submission results")) != -1:
		results_html = html_text[results_start:]
		
		score_match = SCORE_REGEX.search(results_html)
		test_cases_match = TEST_CASES_REGEX.search(results_html)
		
		code_blocks = list()
		
		for code_match in CODE_BLOCK_REGEX.finditer(results_html):
			title = code_match.group(1)
			css_class = code_match.group(2)
			content = html.unescape(code_match.group(3))
			
			code_blocks.append(CodeBlock(title=title, content=content))
			
			# if title == "errors:" and css_class == "cmd":
			# 	compile_error = contents
			# elif "test code" in title and "following error" in title and css_class == "file":
			# 	runtime_error = contents
			# elif ":" in title and css_class == "file":
			# 	failed_test_case = contents
		
		results = SubmitResults(
			points=int(score_match.group(1)) if score_match else None,
			total_points=int(score_match.group(2)) if score_match else None,
			
			test_cases_passed=int(test_cases_match.group(1)) if test_cases_match else 0,
			total_test_cases=int(test_cases_match.group(2)) if test_cases_match else 0,
			
			code_blocks=code_blocks,
		)
	
	file_upload_slots=[UploadSlot(id=m.group(2), name=html.unescape(m.group(1)).strip().rstrip(":")) for m in FILE_UPLOAD_REGEX.finditer(html_text)]
	
	return AtheneResponse(
		results=results,
		file_upload_slots=file_upload_slots
	)

if __name__ == "__main__":
	main()
