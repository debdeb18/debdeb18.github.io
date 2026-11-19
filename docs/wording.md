# Editing the wording

Every title, paragraph, button and prompt on the site has its own box in the **Somewhere Wording** page:
https://claude.ai/artifact/KpWwVdTrnmqt4jFbjYitMe (private to Deby).

Edits save there as you type and show as **waiting**. To put them on the site, ask Claude to "apply the text edits". It:
1. reads the `texts` collection of that page's database (each document: `original`, `value`, `applied`),
2. runs `node tools/texts.mjs extract` for the current file locations, merges in each changed `value` by id, and runs
   `node tools/texts.mjs apply` (each text replaced exactly once in its own file, escaped for where it sits),
3. tests, commits and pushes to `dev`, then marks each applied text's `applied` = `value` in the page's database.

New wording added to the site later: run the extract again and seed the new ids into the page's database.
