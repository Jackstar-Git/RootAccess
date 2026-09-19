## Bugs:
1) When a user doesn't have "create XY" permissions, don't show the sub-page in the sidebar of the admin panel (like create users, create blog, etc...)
## Improvements:
1) Improve the visual design of the filters on both the blogs and projects page (remove horizontal scrollbar, improve multiselect e.g. by removing double scrollbars)
2) Make sure all texts (frontend) are in English
3) On the edit quotes page, add the missing fields for the quotes (date and note)
4) Add an "accessibility center (footer?), where users can disable animations, transitions, etc...
5) Improve design of the "clear logs" button on the logs page.
6) Display the role (+ hierarchy level) of a user under their name in the sidebar
## Additions:
1) An option to reject tracking cookies (functional ones are always on), and if rejected, stop tracking tool 
2) Create a "Me"/"User" page, where the user can edit his Profile on his own (name, password and picture)
3) Under the server-settings page, add a "soft kill" button, that requires admin permissions, which when pressed, shuts down the server immediately. Shows the user a warning beforehand.
4) Theme management: Allow users to add/remove themes (new permission-sets required)
5) Add a "export logs" button on the logs page to download the logs (useful for troubleshooting etc...)