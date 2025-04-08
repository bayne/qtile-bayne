import os
import subprocess

from libqtile import log_utils
from libqtile import widget

logger = log_utils.logger

class GitMineStatus(widget.base.ThreadPoolText):
    defaults = [
        ("update_interval", 30, "Update time in seconds."),
        ("foreground", "ffffff", "foreground color"),
    ]

    def __init__(self, **config):
        widget.base.ThreadPoolText.__init__(self, "", **config)
        self.add_defaults(GitMineStatus.defaults)

    def _poll(self):

        # Define repository status counts
        behind_count = 0
        ahead_count = 0
        conflict_count = 0
        up_to_date_count = 0
        pending_count = 0

        base_dir = os.path.expanduser("~/Code/mine")

        for root, dirs, files in os.walk(base_dir):
            if ".git" in dirs:
                try:
                    repo_dir = root
                    subprocess.run(
                        ["git", "-C", repo_dir, "fetch"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                        )
                    status_output = subprocess.check_output(
                        ["git", "-C", repo_dir, "status", "--porcelain",
                         "--branch"],
                        stderr=subprocess.DEVNULL
                        ).decode()

                    if len(status_output.splitlines()) > 1:
                        pending_count += 1
                    elif "##" in status_output:
                        if ("[ahead" in status_output and "[behind" in
                            status_output):
                            conflict_count += 1
                        elif "[ahead" in status_output:
                            ahead_count += 1
                        elif "[behind" in status_output:
                            behind_count += 1
                        else:
                            up_to_date_count += 1
                except Exception as e:
                    logger.error(
                        f"Error processing git repository at {repo_dir}: {e}"
                    )
        return (f"<b>(↩️{behind_count})(⬆️{ahead_count})(✖️{conflict_count})("
                f"✔️{up_to_date_count})(⋮{pending_count})</b>")

    def poll(self):
        try:
            return self._poll()
        except Exception as e:
            logger.error("Failed to poll for git status", e)
            return f"Error something went wrong"

