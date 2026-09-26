## Bugs:
1) When a user doesn't have "create XY" permissions, don't show the sub-page in the sidebar of the admin panel (like create users, create blog, etc...)
## Improvements:
1) Make sure all texts (frontend) are in English
2) On the edit quotes page, add the missing fields for the quotes (date and note)
3) Add an "accessibility center (footer?), where users can disable animations, transitions, etc...
4) Display the role (+ hierarchy level) of a user under their name in the sidebar
5) Take the blog filter logic form the backend and apply it ot the projects too (copy it)
## Additions:
1) Create a "Me"/"User" page, where the user can edit his Profile on his own (name, password and picture)
2) Under the server-settings page, add a "soft kill" button, that requires admin permissions, which when pressed, shuts down the server immediately. Shows the user a warning beforehand.
3) Theme management: Allow users to add/remove themes (new permission-sets required)
4) Add a "export logs" button on the logs page to download the logs (useful for troubleshooting etc...)