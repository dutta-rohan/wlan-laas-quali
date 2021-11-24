# What are Orchestration Scripts?

Orchestration scripts can enable automating sandbox workflows. You can use orchestration scripts to create setup and teardown procedures as well as other custom workflows that can be made available in the sandbox. Examples include saving and restoring state, starting test traffic, running failover scenarios and more.

# Creating and using orchestration scripts in CloudShell

This procedure shows the basic steps for creating and using orchestration scripts in CloudShell.
1) Create a Python script. You can create a single python script, or a more complex orchestration that uses dependencies, as explained in Scripts Deep Dive .

Tip: It is highly recommended to extend CloudShell's out-of-the-box orchestration scripts as they already contain important orchestration capabilities you'd like to preserve. To do so, log in to CloudShell Portal as Global administrator, in the Manage>Scripts>Blueprint page, download the desired script, make the necessary changes and save the script under a new name.

2. If the script requires the use of Python dependencies, which aren’t available in the public PyPi repository, add them to the local PyPi Server. 

3. Save the script (if it's a single file) or zip the package if it comprises multiple files.
Important: Make sure the script's name is not the same as any of the out-of-the-box scripts.

4. Upload the script to CloudShell. When uploading the script, you can set it as a setup or teardown script, to have it run automatically in the sandbox, or leave it as a manually launched orchestration script.

5. Attach the script to the blueprint. If it’s a setup or teardown script, remove the blueprint’s existing script first.

