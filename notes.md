1. need to make sure that agents can read files outside their own scope
2. also I think it is best to have all file reads and all run commands occur from the wd of the root directory, while children delegations are simply the names of the child from the wd of the parent. This needs to be documented in prompting
3. We need a stronger emphasis on reading context in our prompting.