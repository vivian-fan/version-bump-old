import os
import sys
import shutil
import yaml
import git
import json


def get_remote():
    username = "vivian-fan"
    password = sys.argv[1]
    remote = f"https://{username}:{password}@github.com/vivian-fan/version-bump-old.git"
    return remote


def get_clone_repo(remote, path, branch):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    clone_repo = git.Repo.clone_from(remote, path, branch=branch)
    return clone_repo
  
  
def push_to_origin(target_path, target_branch):
    try:
        repo = git.Repo(target_path)
        repo.git.add(update=True)
        repo.index.commit("delete released intent files")
        repo.git.push("origin", target_branch)
    except Exception as e:
        print("Errors occured while pushing the code", e)

        
def get_version(path, file):
    file += ".yaml"
    with open(path + "/" + file, "r") as spec_file:
        spec_content = yaml.safe_load(spec_file)
    return spec_content["info"]["version"]
  
def getIntentsFromMessage(message):
    intents_str = message.splitlines()[-1].remove("intent: ")
    return json.loads(intents_str)
  
def accumulate_intents(intents_dict, message):
    intents = getIntentsFromMessage(message)
    for fileName, intent from intents.items():
        if fileName not in intents_dict:
          intents_dict[fileName] = intent
        elif intent == "major":
          intents_dict[fileName] = intent
  
def minor_bump(version):
    major, minor, patch = version.split(".")
    return major + "." + str(int(minor) + 1) + "." + patch


def major_bump(version):
    major, minor, patch = version.split(".")
    return str(int(major) + 1) + "." + "0" + "." + patch


def is_less_than(version1, version2):
    version1 = version1.replace(".", "")
    version2 = version2.replace(".", "")
    return version1 < version2


def compute_version(intent, latest_release_version, target_branch_version):
    next_version = None
    if intent == "minor":
        next_version = minor_bump(latest_release_version)
    else:
        next_version = major_bump(latest_release_version)
    if is_less_than(next_version, target_branch_version):
        next_version = target_branch_version
    return next_version
  
  
remote = get_remote()

master_path = "./master"
release_path = "./release"

release_branch = sys.argv[2]

clone_repo_master = get_clone_repo(remote, master_path, "master")
clone_repo_release = get_clone_repo(remote, release_path, release_branch)

master_commits = list(clone_repo_master.iter_commits())
release_commits = list(clone_repo_release.iter_commits())

intents_dict = {}

for commit in master_commit:
   if commit.message.startswith("Bump Version to") and commit not in release_commits:
      accumulate_intents(intents_dict, commit.message)
      
version_matrix = {"include": []}      
      
for fileName, intent in intents_dict.items():
    file = fileName + ".yaml"
    release_version = get_version(release_path, file)
    target_version = get_version(master_path, file)
    next_version = compute_version(intent, release_version, target_version)
    version_matrix["include"].append({"file": file, "version": next_version})

shutil.rmtree(master_path)
shutil.rmtree(release_path)

print(json.dumps(version_matrix))
