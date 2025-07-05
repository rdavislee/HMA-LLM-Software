1. all agents need documentation file added to memory from beginning - DONE
2. master agent needs to be told how to make documentation better. - IN PROGRESS
3. test files would be better off by being adjacent to their implementation folders as opposed to in a test folder - DONE
    a. the current system creates a chokehold for concurrent development because all communication between tests and impls has to go through the root, which makes transfer of information really slow and hard.
4. need to generalize master agents command abilities so that any language could work - DONEish
5. In order for libraries to be super useful, library info needs to be downloaded into some kind of documentation folder for agents to read. - NOT STARTED
6. Agents should be stalled after delegating or spawning. Too much concurrency occurs with the reprompting after delegation/spawning. - DONE
7. Readme documentation could be a lot better, readmes tend to confuse agents because they have outdated information that the agent interprets as correct - IN PROGRESS
8. Agents struggle when a large percent of tests are failing. We need a better way to handle this. - IN PROGRESS
9. Master agent stages need to be more focused on abstraction. - IN PROGRESS
10. Giving master agents the ability to delete files from its memory would probably be good for large projects. - NOT STARTED
11. We NEED to put active children in the prompts. Agents often get confused and redelegate over and over - DONE
12. We should let manager agents run tests, but sparingly. - DONE
13. Prompts NEED to be reduced in size - IN PROGRESS
14. Improve human in the loop for frontend design - NOT STARTED
15. Add a timeout on terminal commands of 5 minutes with a message that it timed out after 300 seconds, don't do it again - NOT STARTED