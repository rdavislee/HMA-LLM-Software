Feedback on base agent implementation, in order of the file. v2

Memory should be dict from filenames to Paths. Context should be dict of previous prompts to responses.

Memory should be a dictionary of filenames to paths to those files. ADD A FUNCTION THAT READS THE CONTENTS OF EVERY FILE IN THE DICTIONARY AND ASSEMBLES A DICTIONARY OF FILENAMES TO FILECONTENTS. We can call this everytime an API call is about to go, in order to have up-to-date memory.

Context should be keys of prompts with values of answers. These represent every API call this agent has made since it was activated.

Personal file should not be optional.

active_tasks should be active task. Agents will only ever have one task, when given another they must have finished their previous.

Set personal file is good, I think we should be actually creating the personal file in execution, which is in the interpreter. We need this to throw like a super mega error if it fails that stops the entire network because it means that something unrelated to the agents actions is broken.

Activate will only work when there is no task and self is not active. Shouldnt be many active tasks, should just be one, and here is where it would set it. Loading context is not necesarry since we can do that before every api call. Lets not call process task or do any actions besides activating the agent here.

Deactivate is very similar, but we need to have a normal error thrown if a child is active. This should basically leave the agent completely blank.

Process task should take in a prompt and will add the prompt to the prompts rep. If stall is false, calls API call. Returns nothing.

There should be an API call function. It first loads context/memory and sets the stall rep to true. Then it does the API call with all the prompts from the prompt field concatenated (perhaps numbered?) and with context/memory. Then, it calls the prompter recieve function with its output as an input. The prompter, after parsing the output, will process the call, and then update the agents memory and context. After being sure there are no dependencies, the prompter will set stall to false. If there is nothing else in the queue after a self prompting action, the prompter will add another prompt such as "Action complete!" After allat, if there is something in the prompting queue, it will call the API call.

Read file should be adding a pointer to the file to read to the memory.

Perhaps instead of using update personal file, we can just always have a pointer to the personal file in memory, so its constantly automatically updated.

No need for run_command, this will be done in interpreter and output provided in subsequent prompt.

No need for send message, reveive message, or send result, prompter will handle message sending.

Load context should be adding the random shit to memory that it has at the beginning, such as personal file.

The getters at the bottom are good, will probably need to be changed with the other changes. Get context string should load all memory, all chat history in context, and put it into a readable string format. This should make it so the first prompt which explains its entire purpose only ever has to be sent on the first time, as itll be in the context from then on. We could explain how file reads and codebase structure in memory are automatically updated.