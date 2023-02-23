"""
Frontend for 'Supercomputer on the Cloud'

%load_ext autoreload
%autoreload 2
"""

# %% Modules

import time
import threading
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from tkinter.font import *
from utilities import *

# %% Formatting

get_status_running = False

# %% Functions

def frame_key_press(event):
    """
    Process key inputs for the frame
    """
    if event.char == "q":
        window.destroy()

def get_status():
    """
    Query status of the cluster
    """
    while get_status_running:
        response = bash("oc get mpijobs --no-headers -o custom-columns=\":.metadata.name,:.status.replicaStatuses.Launcher.active,:.status.replicaStatuses.Worker.active\"")

        if len(response) > 0:
            for mpijob in response:
                columns = mpijob.split()
                response = bash("oc get pods | grep %s" % (columns[0]))
    
                if len(response) == 0:
                    bash("helm uninstall %s" % (columns[0]))

        time.sleep(0.5)

def update_submission_status(message):
    """
    Update the submission status entry
    """
    submission_status_entry.delete(0, END)
    submission_status_entry.insert(END, message)

def submit_job():
    """
    Sends job to cluster
    """
    update_submission_status("")

    job_name = job_name_entry.get()

    if len(job_name) == 0:
        update_submission_status("Job name is invalid")
        return

    num_ranks = num_ranks_entry.get()

    if not num_ranks.isnumeric():
        update_submission_status("Number of ranks is not a number")
        return

    cpus_per_rank = cpus_per_rank_entry.get()

    if not cpus_per_rank[:-1].isnumeric():
        update_submission_status("CPUs per rank is not a number")
        return

    gpus_per_rank = gpus_per_rank_entry.get()

    if not gpus_per_rank.isnumeric():
        update_submission_status("GPUs per rank is not a number")
        return

    mem_per_rank = mem_per_rank_entry.get()

    if not mem_per_rank.isnumeric():
        update_submission_status("Memory per rank is not a number")
        return

    job_commands = job_commands_entry.get(1.0, END)

    if len(job_commands) == 1:
        update_submission_status("No job commands provided")
        return

    helm_submission  = "helm upgrade --install --wait "
    helm_submission += "--set jobName=\"%s\" " % (job_name)
    helm_submission += "--set namespace=\"%s\" " % ("default")
    helm_submission += "--set containerImage=mpioperator/tensorflow-benchmarks "
    helm_submission += "--set numRanks=%s " % (num_ranks)
    helm_submission += "--set numCpusPerRank=%s " % (cpus_per_rank)
    helm_submission += "--set numGpusPerRank=%s " % (gpus_per_rank)
    helm_submission += "--set totalMemoryPerRank=%sMi " % (mem_per_rank)

    for idx, command in enumerate(job_commands.split()):
        helm_submission += "--set bashCommands[%d]=\"%s\" " % (idx, command)

    helm_submission += "%s mpi-chart" % (job_name)

    bash(helm_submission)

# %% Main program

if __name__ == "__main__":
    window = Tk()
    window.geometry("680x340")

    font = Font(family = "Arial", size = 16)

    frame = Frame(window)
    frame.bind("<KeyPress>", frame_key_press)
    frame.pack()
    frame.focus_set()

    x_start = 70
    y_start = 10
    entry_width = 120
    entry_height = 30
    input_width = 400
    input_height = 100
    output_width = 400
    output_height = 100
    button_width = 120
    button_height = 30

    # Job name
    job_name_label = Label(window, text = "MPI Job Name:")
    job_name_label["font"] = font
    job_name_label.place(x = x_start + 20, y = y_start + 0 * entry_height)

    job_name_entry = Entry(window)
    job_name_entry["font"] = font
    job_name_entry["justify"] = "right"
    job_name_entry.place(width = entry_width, x = x_start + 160, y = y_start + 0 * entry_height)

    # Number of ranks
    num_ranks_label = Label(window, text = "Number of Ranks:")
    num_ranks_label["font"] = font
    num_ranks_label.place(x = x_start, y = y_start + 1 * entry_height)

    num_ranks_entry = Entry(window)
    num_ranks_entry["font"] = font
    num_ranks_entry["justify"] = "right"
    num_ranks_entry.place(width = entry_width, x = x_start + 160, y = y_start + 1 * entry_height)

    # CPUs per rank
    cpus_per_rank_label = Label(window, text = "CPUs per Rank:")
    cpus_per_rank_label["font"] = font
    cpus_per_rank_label.place(x = x_start + 15, y = y_start + 2 * entry_height)

    cpus_per_rank_entry = Entry(window)
    cpus_per_rank_entry["font"] = font
    cpus_per_rank_entry["justify"] = "right"
    cpus_per_rank_entry.place(width = entry_width, x = x_start + 160, y = y_start + 2 * entry_height)

    # GPUs per rank
    gpus_per_rank_label = Label(window, text = "GPUs per Rank:")
    gpus_per_rank_label["font"] = font
    gpus_per_rank_label.place(x = x_start + 15, y = y_start + 3 * entry_height)

    gpus_per_rank_entry = Entry(window)
    gpus_per_rank_entry["font"] = font
    gpus_per_rank_entry["justify"] = "right"
    gpus_per_rank_entry.place(width = entry_width, x = x_start + 160, y = y_start + 3 * entry_height)

    # Memory per rank
    mem_per_rank_label = Label(window, text = "Memory per Rank (MB):")
    mem_per_rank_label["font"] = font
    mem_per_rank_label.place(x = x_start - 50, y = y_start + 4 * entry_height)

    mem_per_rank_entry = Entry(window)
    mem_per_rank_entry["font"] = font
    mem_per_rank_entry["justify"] = "right"
    mem_per_rank_entry.place(width = entry_width, x = x_start + 160, y = y_start + 4 * entry_height)

    # Job commands
    job_commands_label = Label(window, text = "Job commands:")
    job_commands_label["font"] = font
    job_commands_label.place(x = x_start + 15, y = y_start + 0.35 * input_height + 5 * entry_height)

    job_commands_entry = Text(window)
    job_commands_entry["font"] = font
    job_commands_entry.place(width = input_width, height = input_height, x = x_start + 160, y = y_start + 5 * entry_height)

    # Submit jobs
    submit_job_label = Label(window, text = "Submit job:")
    submit_job_label["font"] = font
    submit_job_label.place(x = x_start + 55, y = y_start + input_height + 5 * entry_height)

    submit_job_entry = Button(window, command = submit_job)
    submit_job_entry["font"] = font
    submit_job_entry["text"] = "Submit"
    submit_job_entry.place(width = button_width, height = button_height, x = x_start + 160, y = y_start + input_height + 5 * entry_height)

    # Submission status
    submission_status_label = Label(window, text = "Submission status:")
    submission_status_label["font"] = font
    submission_status_label.place(x = x_start - 8, y = y_start + input_height + 6 * entry_height)

    submission_status_entry = Entry(window)
    submission_status_entry["font"] = font
    submission_status_entry["justify"] = "right"
    submission_status_entry.place(width = input_width, height = button_height, x = x_start + 160, y = y_start + input_height + 6 * entry_height)

    # Prefilling
    job_name_entry.insert(END, "my-job-1")
    num_ranks_entry.insert(END, "2")
    cpus_per_rank_entry.insert(END, "500m")
    gpus_per_rank_entry.insert(END, "0")
    mem_per_rank_entry.insert(END, "512")
    job_commands_entry.insert(END, "mpirun --allow-run-as-root -n 2 hostname")

    # Main loop
    get_status_running = True

    status_thread = threading.Thread(target = get_status)
    status_thread.start()

    window.mainloop()

    get_status_running = False
    status_thread.join()

# %% End of program
