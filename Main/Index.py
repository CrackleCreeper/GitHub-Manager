import json

from github import Github, Auth
import os
f = open("Settings.json")
Settings = json.load(f)
f.close()
dir = Settings["working_dir"]
auth = Auth.Token(Settings["auth_token"])
g = Github(auth=auth)
existing_repos = []
list_of_paths = []
list_of_paths2 = []
check_for_deletion = []
user = g.get_user()
message: str = Settings["commit_message"]
delete_message = Settings["delete_message"]
update_message = Settings["update_message"]
newly_created_message = Settings["newly_created_message"]


def commit_files(p, project, repo):
    for item in os.listdir(p):
        file_path = os.path.join(p, item)

        if os.path.isfile(file_path):
            if not item == "package-lock.json":
                with open(file_path, 'r') as f:
                    contents = f.read()
                    pa = file_path.replace(
                        dir + project + "\\",
                        "")
                    paa = pa.replace("\\", "/")
                    repo.create_file(paa, message, contents, "main")
        if os.path.isdir(file_path):
            if not item == "node_modules":
                commit_files(file_path, project, repo)


def edit_files(p, repot, project):
    contents = repot.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repot.get_contents(file_content.path))
        else:
            list_of_paths.append(file_content.path)

    for item in os.listdir(p):
        file_path = os.path.join(p, item)

        if os.path.isfile(file_path):
            if not item == "package-lock.json":
                with open(file_path, 'r') as f:
                    content = f.read()
                    pa = file_path.replace(
                        dir + project + "\\",
                        "")
                    paa = pa.replace("\\", "/")

                    try:
                        contents_of_filet = repot.get_contents(paa)
                        contents_of_file = str(contents_of_filet.decoded_content)
                        new_content = contents_of_file[2:-1]
                        if new_content != content:
                            print("Found a file to update.")
                            repot.update_file(paa, update_message, content, contents_of_filet.sha, branch="main")

                        check_for_deletion.append(paa)
                    except:
                        # Newly Created file found.
                        print("Newly created file found.")
                        paa = pa.replace("\\", "/")
                        with open(file_path, 'r') as f:
                            content = f.read()
                            repot.create_file(paa, newly_created_message, content, "main")

        if os.path.isdir(file_path):
            if item != "node_modules":
                edit_files(file_path, repot, project)


def delete_files(repot):
    deleted_files = set(list_of_paths).difference(check_for_deletion)

    if deleted_files != set():
        print("Deleting a File.")
        for file in deleted_files:
            cont = repot.get_contents(file)
            repot.delete_file(file, delete_message, cont.sha, branch="main")


def update_repos():
    user_repos = user.get_repos()
    for r in user_repos:

        existing_repos.append(r.name)

    os.chdir(dir)

    for project in os.listdir():
        if project not in existing_repos:
            print("Currently pushing " + project + " to GitHub.")
            repo = user.create_repo(project, f"A new repository automatically created to push {project} to github", private=True)
            os.chdir(os.path.join(dir, project))

            commit_files(os.getcwd(), project, repo)
        else:
            repository = user.get_repo(project)
            print('The repo ' + project + ' already exists on GitHub.')
            edit_files(os.getcwd(), repository, project)
            delete_files(repository)

    g.close()


update_repos()