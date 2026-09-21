#!/usr/bin/env python
__version__ = "1.1.0"
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import requests as r
from colorama import Fore

w = Fore.WHITE
rd = Fore.RED
bl = Fore.BLACK
gr = Fore.GREEN
ylw = Fore.YELLOW
reset = Fore.RESET

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, check=True)

def refresh():
    url = "https://raw.githubusercontent.com/wxwreak/ppush/refs/heads/main/ppush.py"
    resp = r.get(url)
    if resp.status_code == 200:
        with open("ppush.py", "wb") as f:
            f.write(resp.content)
        print("Succesfully fetch update")
    else:
        print("Failed to fetch update")
        return
    ppush_f = "ppush.py"
    ppush_alias = "ppush"
    target = Path.home() / ".local" / "bin"
    target.mkdir(parents=True, exist_ok=True)
    st = os.stat(ppush_f)
    os.chmod(ppush_f, st.st_mode | stat.S_IEXEC)
    shutil.copy(ppush_f, target / ppush_alias)
    print(f"{ppush_f} refreshed")

def show_ver():
    print(f"Version: [{__version__}]")

def ppush():
    curr_dir = os.getcwd()
    
    if not os.path.exists(os.path.join(curr_dir, '.git')):
        print(f"{bl}[{w}Error{bl}] {rd}In folder [{curr_dir}] is no .git{reset}")
        wantgit = input("Do you want to initialize git here? (y/n): ").lower()
        
        if wantgit == 'y':
            repo_url = input("Repo URL (ex. https://github.com/wxwreak/myrepo.git): ")
            run_cmd("git init")
            if repo_url:
                run_cmd(f"git remote add origin {repo_url}")
                run_cmd("git branch -M main")
                print(f"{bl}[{w}Success{bl}] {gr}Successfully Initialized git and added remote origin{reset}")
            else:
                print(f"{bl}[{w}Warning{bl}] {ylw}Git initialized without remote (no URL provided){reset}")
        else:
            print(f"{bl}[{w}Error{bl}] {rd}Operation denied. Exiting...{reset}")
            return
            
    else:
        try:
            remotes = subprocess.check_output(["git", "remote"]).decode().strip()    
            if "origin" not in remotes:
                print(f"{bl}[{w}Warning{bl}] {ylw}Git folder exists, but no remote 'origin' found.{reset}")
                repo_url = input("Please enter Repo URL (ex. https://github.com/wxwreak/myrepo.git): ")
                if repo_url:
                    run_cmd(f"git remote add origin {repo_url}")
                    run_cmd("git branch -M main")
                    print(f"{bl}[{w}Success{bl}] {gr}Remote 'origin' added and branch set to main.{reset}")
                else:
                    print(f"{bl}[{w}Error{bl}] {rd}No remote URL provided. Push will likely fail.{reset}")
            else:
                print(f"{bl}[{w}Info{bl}] {gr}Git repository and remote origin are ready.{reset}")
        except Exception as e:
            print(f"{bl}[{w}Error{bl}] {rd}Error checking git remotes: {e}{reset}")

    if len(sys.argv) > 1:
        commit_msg = " ".join(sys.argv[1:])
    else:
        commit_msg = input("Enter commit msg: ")
        
    if not commit_msg:
        commit_msg = "Commit Initalize: ppush"
    
    try:
        run_cmd("git add .")
        status = subprocess.check_output("git status --porcelain", shell=True).decode().strip()
        if not status:
            print(f"{bl}[{w}Info{bl}] {w}No changes to commit.{reset}")
            return
        
        run_cmd(f'git commit -m "{commit_msg}"')
        print(f"{bl}[{w}Success{bl}] {gr}Successfully Committed with message: {commit_msg}{reset}")        
        branch = subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=True).decode().strip() 
        print(f"{bl}[{w}Info{bl}] {w}Pushing to branch [{branch}]...{reset}")
        
        try:
            run_cmd(f"git push -u origin {branch}")
            print(f"{bl}[{w}Success{bl}] {gr}Successfully Pushed to GitHub{reset}")
        except subprocess.CalledProcessError:
            print(f"\n{bl}[{w}Warning{bl}] {ylw}Remote contains work that you do not have locally.{reset}")
            wantforcepush = input(f"{w}Do you want to force push? (y/n): {reset}").lower()
            if wantforcepush == 'y':
                print(f"{bl}[{w}Info{bl}] {w}Force pushing...{reset}")
                run_cmd(f"git push -u origin {branch} --force")
                print(f"{bl}[{w}Success{bl}] {gr}Successfully Force Pushed to GitHub{reset}")
            else:
                print(f"{bl}[{w}Info{bl}] {w}Push aborted. You might need to 'git pull' first.{reset}")

    except subprocess.CalledProcessError as e:
        print(f"{bl}[{w}Error{bl}] {rd}Git Error: {e}{reset}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        ppush()
    else:
        arg = sys.argv[1]
        
        if arg == "--refresh":
            refresh()
        elif arg == "--help":
            commands = """
[ppush] Standard push with interactive commit message
ppush [--help] Show this help message
ppush [--refresh] Fetch new version from GitHub
ppush [--version] Shows current version
            """
            print(commands)
        elif arg == "--version":
            show_ver()
        else:
            ppush()
